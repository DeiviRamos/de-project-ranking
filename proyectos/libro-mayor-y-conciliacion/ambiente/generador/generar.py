#!/usr/bin/env python3
"""Generador de datos sintéticos — Libro Mayor y Conciliación.

Simula una fintech ficticia ("Pagoflux SpA") que procesa pagos de comercios y
produce, por día, los archivos que entregan tres fuentes:

  sistema_operativo/  exportaciones diarias de movimientos del sistema propio
  pasarela/           reportes de liquidación de la pasarela de pago con tarjeta
  banco/              extractos de la cuenta corriente
  maestros/           comercios (foto diaria), plan de cuentas, tipo de cambio, feriados

Todo es sintético y reproducible con la semilla. Solo usa la biblioteca estándar
(más el paquete `tzdata` si el sistema no trae la base de zonas horarias).

Uso rápido:
    python generar.py --salida ../data
    python generar.py --salida /tmp/datos --dias 60 --escala 10 --semilla 7
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import string
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_LOCAL = ZoneInfo("America/Santiago")
UTC = timezone.utc

# Feriados bancarios del mundo simulado (MM-DD, se repiten todos los años).
FERIADOS_MMDD = [
    "01-01", "05-01", "05-21", "06-20", "07-16", "08-15",
    "09-18", "09-19", "10-12", "10-31", "11-01", "12-08", "12-25",
]

PLANES = {"BASICO": Decimal("3.49"), "PRO": Decimal("2.89"), "ENTERPRISE": Decimal("1.99")}
RUBROS = ["Alimentos", "Vestuario", "Tecnología", "Salud", "Educación", "Hogar",
          "Deportes", "Servicios profesionales", "Turismo", "Mascotas"]
PREFIJOS = ["Comercial", "Distribuidora", "Inversiones", "Servicios", "Tienda", "Importadora"]
NOMBRES = ["Cerro Azul", "Río Claro", "Los Aromos", "Bahía Norte", "Las Quilas", "Altamira",
           "Puerto Lindo", "Valle Sereno", "Monte Quieto", "Laguna Verde", "El Peumo",
           "Campo Dorado", "Isla Mayor", "Las Brisas", "Piedra Roja", "Cumbre Alta"]
SUFIJOS = ["SpA", "Ltda.", "E.I.R.L.", "S.A."]

TASA_PASARELA = Decimal("0.0149")
IVA = Decimal("0.19")
COMISION_TRANSF_BANCO = 300
COMISION_MANTENCION_BANCO = 25000
CARGO_CONTRACARGO = 15000
SALDO_INICIAL_BANCO = 150_000_000


# --------------------------------------------------------------------------- utilidades

def es_habil(d: date) -> bool:
    return d.weekday() < 5 and d.strftime("%m-%d") not in FERIADOS_MMDD


def sig_habil(d: date) -> date:
    d += timedelta(days=1)
    while not es_habil(d):
        d += timedelta(days=1)
    return d


def redondear(x: Decimal, dec: int = 0) -> Decimal:
    q = Decimal(1).scaleb(-dec)
    return x.quantize(q, rounding=ROUND_HALF_UP)


def dv_rut(cuerpo: int) -> str:
    s, m = 0, 2
    for c in reversed(str(cuerpo)):
        s += int(c) * m
        m = 2 if m == 7 else m + 1
    r = 11 - s % 11
    return {11: "0", 10: "K"}.get(r, str(r))


def fmt_rut(cuerpo: int, con_puntos: bool = True) -> str:
    c = f"{cuerpo:,}".replace(",", ".") if con_puntos else str(cuerpo)
    return f"{c}-{dv_rut(cuerpo)}"


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def local_naive(dt: datetime) -> str:
    return dt.astimezone(TZ_LOCAL).strftime("%Y-%m-%d %H:%M:%S")


def fecha_local(dt: datetime) -> date:
    return dt.astimezone(TZ_LOCAL).date()


def fmt_monto(m: Decimal, moneda: str | None) -> str:
    return str(redondear(m, 2 if moneda == "USD" else 0))


def fmt_banco(n: int) -> str:
    return f"{n:,}".replace(",", ".") if n else ""


# --------------------------------------------------------------------------- modelo

@dataclass
class Comercio:
    id: str
    rut_cuerpo: int
    razon_social: str
    rubro: str
    plan: str
    estado: str
    fecha_alta: date
    actualizado_en: datetime
    # historial de (desde, plan) para saber la tasa vigente
    historial_plan: list = field(default_factory=list)

    def tasa_en(self, t: datetime) -> Decimal:
        plan = self.historial_plan[0][1]
        for desde, p in self.historial_plan:
            if desde <= t:
                plan = p
        return PLANES[plan]

    def tasa_anterior(self, t: datetime) -> Decimal:
        planes = [p for desde, p in self.historial_plan if desde <= t]
        return PLANES[planes[-2]] if len(planes) >= 2 else PLANES[planes[-1]]


class Generador:
    def __init__(self, a: argparse.Namespace):
        self.a = a
        self.rng = random.Random(a.semilla)          # flujo base
        self.rd = random.Random(a.semilla + 10_007)  # decisiones de imperfecciones
        self.p = a.pct_defectos / 100.0
        self.estructurales = a.pct_defectos > 0
        self.desde = a.desde
        self.hasta = a.desde + timedelta(days=a.dias - 1)
        self.salida = Path(a.salida)
        self.registro: list[dict] = []
        self.ids_usados: set[str] = set()

        # estado
        self.comercios: list[Comercio] = []
        self.versiones_ops: list[dict] = []            # filas del sistema operativo
        self.pagos: dict[str, dict] = {}
        self.devengos: dict[tuple, Decimal] = defaultdict(Decimal)  # (comercio, fecha_local) -> CLP
        self.liq: dict[date, list] = defaultdict(list)  # fecha liquidación -> filas pasarela
        self.banco: dict[date, list] = defaultdict(list)  # fecha contable -> filas
        self.tc: dict[date, Decimal] = {}

        # imperfecciones estructurales (fechas elegidas con rd)
        dias = [self.desde + timedelta(days=i) for i in range(a.dias)]
        habiles = [d for d in dias if es_habil(d)]
        mitad = habiles[len(habiles) // 2:] if habiles else []
        self.dia_pico = self.rd.choice(dias[1:]) if self.estructurales and len(dias) > 1 else None
        self.fecha_cambio_esquema = (self.rd.choice(mitad[:3]) if self.estructurales and mitad else None)
        self.dia_sin_extracto = (self.rd.choice(habiles[2:-2]) if self.estructurales and len(habiles) > 5 else None)
        self.dia_reenvio = self.rd.choice(dias[:-1]) if self.estructurales and len(dias) > 2 else None
        self.dia_sin_comercios = self.rd.choice(dias[1:]) if self.estructurales and len(dias) > 3 else None
        self.dia_retencion = (self.rd.choice(habiles[1:]) if self.estructurales and len(habiles) > 3 else None)

    # ----------------------------------------------------------------- helpers
    def defecto(self, factor: float = 1.0) -> bool:
        return self.rd.random() < self.p * factor

    def anotar(self, tipo: str, archivo: str, clave: str, detalle: str = "") -> None:
        self.registro.append({"tipo": tipo, "archivo": archivo, "clave": clave, "detalle": detalle})

    def nuevo_id(self, prefijo: str, largo: int = 10) -> str:
        alfabeto = string.digits + string.ascii_uppercase
        while True:
            v = prefijo + "".join(self.rng.choice(alfabeto) for _ in range(largo))
            if v not in self.ids_usados:
                self.ids_usados.add(v)
                return v

    def momento(self, d: date) -> datetime:
        """Instante del día local d, con más actividad entre 9 y 23 h."""
        hora = min(23, max(0, int(self.rng.gauss(15, 4.5))))
        t = datetime.combine(d, time(hora, self.rng.randrange(60), self.rng.randrange(60)), TZ_LOCAL)
        return t

    def tipo_cambio(self, d: date) -> Decimal:
        while d not in self.tc:
            d -= timedelta(days=1)
        return self.tc[d]

    # ----------------------------------------------------------------- maestros
    def crear_tipo_cambio(self) -> None:
        d = self.desde - timedelta(days=15)
        v = Decimal("942.50")
        fin = self.hasta + timedelta(days=15)
        while d <= fin:
            if es_habil(d):
                v = redondear(v * Decimal(str(1 + self.rng.gauss(0, 0.004))), 2)
                self.tc[d] = v
            d += timedelta(days=1)

    def crear_comercios(self) -> None:
        n = max(20, int(80 * self.a.escala))
        inicio = datetime.combine(self.desde - timedelta(days=1), time(23, 0), TZ_LOCAL)
        for i in range(n):
            self.comercios.append(self._comercio(i + 1, inicio, alta=self.desde - timedelta(days=self.rng.randint(30, 900))))

    def _comercio(self, num: int, t: datetime, alta: date) -> Comercio:
        plan = self.rng.choices(list(PLANES), weights=[60, 30, 10])[0]
        nombre = f"{self.rng.choice(PREFIJOS)} {self.rng.choice(NOMBRES)} {self.rng.choice(SUFIJOS)}"
        c = Comercio(
            id=f"COM-{num:05d}", rut_cuerpo=self.rng.randint(76_000_000, 77_999_999),
            razon_social=nombre, rubro=self.rng.choice(RUBROS), plan=plan, estado="ACTIVO",
            fecha_alta=alta, actualizado_en=t,
        )
        c.historial_plan.append((datetime(2000, 1, 1, tzinfo=UTC), plan))
        return c

    def evolucionar_comercios(self, d: date) -> None:
        for c in self.comercios:
            r = self.rng.random()
            if r < 0.012 and c.estado == "ACTIVO":
                nuevo = self.rng.choice([p for p in PLANES if p != c.plan])
                t = self.momento(d)
                c.plan, c.actualizado_en = nuevo, t
                c.historial_plan.append((t, nuevo))
            elif r < 0.016:
                c.estado = "SUSPENDIDO" if c.estado == "ACTIVO" else "ACTIVO"
                c.actualizado_en = self.momento(d)
        if self.rng.random() < 0.25:
            t = self.momento(d)
            self.comercios.append(self._comercio(len(self.comercios) + 1, t, alta=d))

    def foto_comercios(self, d: date) -> None:
        nombre = f"maestros/comercios/comercios_{d.isoformat()}.csv"
        if d == self.dia_sin_comercios:
            self.anotar("archivo_faltante", nombre, d.isoformat(), "no se emite la foto del día")
            return
        filas = []
        for c in self.comercios:
            if c.fecha_alta > d:
                continue
            con_puntos = True
            if self.defecto(0.5):
                con_puntos = False
                self.anotar("rut_formato_distinto", nombre, c.id)
            filas.append({
                "id_comercio": c.id, "rut": fmt_rut(c.rut_cuerpo, con_puntos),
                "razon_social": c.razon_social, "rubro": c.rubro, "plan": c.plan,
                "tasa_comision_pct": str(PLANES[c.plan]), "estado": c.estado,
                "fecha_alta": c.fecha_alta.isoformat(), "actualizado_en": iso_utc(c.actualizado_en),
            })
            if self.defecto(0.2):
                filas.append(dict(filas[-1]))
                self.anotar("duplicado", nombre, c.id)
        self.escribir_csv(nombre, filas)

    # ----------------------------------------------------------------- operaciones
    def fila_ops(self, **kw) -> dict:
        base = {"id_movimiento": None, "tipo": None, "id_comercio": None, "id_movimiento_origen": "",
                "medio": "", "monto": None, "moneda": "CLP", "estado": "APROBADO",
                "referencia_externa": "", "creado_en": None, "actualizado_en": None}
        base.update(kw)
        return base

    def emitir(self, fila: dict) -> None:
        self.versiones_ops.append(fila)

    def clp(self, monto: Decimal, moneda: str, d: date) -> Decimal:
        return monto if moneda == "CLP" else redondear(monto * self.tipo_cambio(d), 0)

    def simular_dia(self, d: date) -> None:
        self.evolucionar_comercios(d)
        n = int(self.a.movs_por_dia * self.a.escala)
        if d == self.dia_pico:
            n *= 5
            self.anotar("pico_volumen", f"sistema_operativo/movimientos_{d.isoformat()}.csv", d.isoformat(), "x5")
        activos = [c for c in self.comercios if c.estado == "ACTIVO" and c.fecha_alta <= d]
        for _ in range(n):
            self.simular_pago(d, self.rng.choice(activos))

    def simular_pago(self, d: date, com: Comercio) -> None:
        t = self.momento(d)
        medio = "TARJETA" if self.rng.random() < 0.8 else "TRANSFERENCIA"
        moneda = "USD" if medio == "TARJETA" and self.rng.random() < 0.03 else "CLP"
        if moneda == "USD":
            monto = redondear(Decimal(str(self.rng.lognormvariate(3.4, 0.8))), 2)
        else:
            monto = redondear(Decimal(str(self.rng.lognormvariate(10.0, 1.0))), 0)
            monto = max(monto, Decimal(500))
        r = self.rng.random()
        estado = "APROBADO" if r < 0.88 else ("RECHAZADO" if r < 0.96 else "PENDIENTE")
        ref = self.nuevo_id("PSR-", 8) if medio == "TARJETA" else self.nuevo_id("TRF-", 9)
        pid = self.nuevo_id("MOV-")
        pago = {"id": pid, "comercio": com, "medio": medio, "moneda": moneda, "monto": monto,
                "ref": ref, "creado": t, "reembolsado": Decimal(0)}
        self.pagos[pid] = pago
        self.emitir(self.fila_ops(id_movimiento=pid, tipo="PAGO", id_comercio=com.id, medio=medio,
                                  monto=monto, moneda=moneda, estado=estado, referencia_externa=ref,
                                  creado_en=t, actualizado_en=t))
        final, t_final = estado, t
        if estado == "PENDIENTE":
            t_final = t + timedelta(minutes=self.rng.randint(10, 30 * 60))
            final = "APROBADO" if self.rng.random() < 0.7 else "RECHAZADO"
            self.emitir(self.fila_ops(id_movimiento=pid, tipo="PAGO", id_comercio=com.id, medio=medio,
                                      monto=monto, moneda=moneda, estado=final, referencia_externa=ref,
                                      creado_en=t, actualizado_en=t_final))
        if final == "APROBADO":
            self.aprobar_pago(pago, t_final)
        elif medio == "TRANSFERENCIA" and self.defecto(0.3):
            # el dinero llegó al banco aunque el sistema lo marcó rechazado
            fb = self.fecha_banco(t_final)
            self.banco[fb].append(("TRANSF RECIBIDA", ref, 0, int(monto)))
            self.anotar("abono_sin_pago_aprobado", f"banco ({fb})", ref, pid)

    def fecha_banco(self, t: datetime) -> date:
        loc = t.astimezone(TZ_LOCAL)
        d = loc.date()
        if es_habil(d) and loc.hour < 18:
            return d
        return sig_habil(d)

    def aprobar_pago(self, pago: dict, t: datetime) -> None:
        com, moneda, monto = pago["comercio"], pago["moneda"], pago["monto"]
        tasa = com.tasa_en(t)
        if com.tasa_anterior(t) != tasa and self.defecto(3):
            tasa = com.tasa_anterior(t)
            self.anotar("comision_tasa_desactualizada", "sistema_operativo", pago["id"], str(tasa))
        comision = redondear(monto * tasa / 100, 2 if moneda == "USD" else 0)
        cid = self.nuevo_id("MOV-")
        self.emitir(self.fila_ops(id_movimiento=cid, tipo="COMISION", id_comercio=com.id,
                                  id_movimiento_origen=pago["id"], monto=comision, moneda=moneda,
                                  creado_en=t, actualizado_en=t))
        dl = fecha_local(t)
        self.devengos[(com.id, dl)] += self.clp(monto - comision, moneda, dl)

        if pago["medio"] == "TARJETA":
            self.liquidar(pago["ref"], t, "CAPTURA", moneda, monto, pago["id"])
        else:
            fb = self.fecha_banco(t)
            doc = pago["ref"]
            if self.defecto(0.6):
                doc = ""
                self.anotar("abono_sin_referencia", f"banco ({fb})", pago["ref"], pago["id"])
            self.banco[fb].append(("TRANSF RECIBIDA", doc, 0, int(monto)))

        if self.rng.random() < 0.05:
            self.reembolsar(pago, t + timedelta(hours=self.rng.randint(20, 120)))

    def reembolsar(self, pago: dict, t: datetime) -> None:
        monto = pago["monto"]
        if self.rng.random() > 0.7:
            monto = redondear(monto * Decimal(str(self.rng.uniform(0.2, 0.9))), 2 if pago["moneda"] == "USD" else 0)
        origen = pago["id"]
        if self.defecto(1.5):
            monto = redondear(pago["monto"] * Decimal("1.5"), 2 if pago["moneda"] == "USD" else 0)
            self.anotar("reembolso_mayor_al_pago", "sistema_operativo", origen, str(monto))
        elif self.defecto(1.0):
            origen = "MOV-" + "".join(self.rd.choice(string.digits) for _ in range(10))
            self.anotar("reembolso_origen_inexistente", "sistema_operativo", pago["id"], origen)
        rid = self.nuevo_id("MOV-")
        ref = pago["ref"] if pago["medio"] == "TARJETA" else self.nuevo_id("DEV-", 9)
        self.emitir(self.fila_ops(id_movimiento=rid, tipo="REEMBOLSO", id_comercio=pago["comercio"].id,
                                  id_movimiento_origen=origen, medio=pago["medio"], monto=monto,
                                  moneda=pago["moneda"], referencia_externa=ref, creado_en=t, actualizado_en=t))
        dl = fecha_local(t)
        self.devengos[(pago["comercio"].id, dl)] -= self.clp(monto, pago["moneda"], dl)
        if pago["medio"] == "TARJETA":
            self.liquidar(ref, t, "DEVOLUCION", pago["moneda"], -monto, rid)
        else:
            self.banco[self.fecha_banco(t)].append((f"TRANSF A TERCEROS {ref}", ref, int(monto), 0))

    # ----------------------------------------------------------------- pasarela
    def liquidar(self, ref: str, t: datetime, tipo: str, moneda: str, monto: Decimal, mov: str) -> None:
        if tipo == "CAPTURA" and self.defecto(0.5):
            self.anotar("captura_no_liquidada", "pasarela", ref, mov)
            return
        fl = sig_habil(fecha_local(t))
        if self.rng.random() < 0.1:
            fl = sig_habil(fl)
        tc = Decimal(1)
        if moneda == "USD":
            tc = redondear(self.tipo_cambio(fecha_local(t)) * Decimal("0.985"), 2)
        bruto = redondear(monto * tc, 0)
        if self.defecto(0.4):
            bruto += self.rd.choice([-1, 1])
            self.anotar("diferencia_redondeo", f"pasarela ({fl})", ref, mov)
        fila = {"ref": ref, "t": t, "tipo": tipo, "moneda": moneda, "monto": monto, "tc": tc, "bruto": bruto}
        self.liq[fl].append(fila)
        if tipo == "CAPTURA" and self.defecto(0.15):
            self.liq[sig_habil(fl)].append(dict(fila))
            self.anotar("liquidacion_duplicada", f"pasarela ({sig_habil(fl)})", ref, mov)
        if tipo == "CAPTURA" and self.defecto(0.1):
            fc = sig_habil(sig_habil(sig_habil(fl)))
            self.liq[fc].append({**fila, "tipo": "CONTRACARGO", "bruto": -bruto, "t": t})
            self.anotar("contracargo", f"pasarela ({fc})", ref, mov)

    def escribir_pasarela(self) -> None:
        for fl in sorted(self.liq):
            if fl > self.hasta or fl < self.desde:
                continue
            filas_in = self.liq[fl]
            if self.estructurales and self.rd.random() < 0.6:
                t = datetime.combine(fl - timedelta(days=1),
                                     time(self.rd.randrange(9, 22), self.rd.randrange(60)), TZ_LOCAL)
                bruto = redondear(Decimal(str(self.rd.lognormvariate(10, 0.8))), 0)
                ref = "PSR-" + "".join(self.rd.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                filas_in.append({"ref": ref, "t": t, "tipo": "CAPTURA", "moneda": "CLP",
                                 "monto": bruto, "tc": Decimal(1), "bruto": bruto})
                self.anotar("transaccion_fantasma", f"pasarela ({fl})", ref)
            nuevo = self.fecha_cambio_esquema is not None and fl >= self.fecha_cambio_esquema
            id_liq = f"LIQ-{fl.strftime('%Y%m%d')}"
            filas, total = [], 0
            for f in filas_in:
                bruto = f["bruto"]
                if f["tipo"] == "CAPTURA":
                    com = redondear(bruto * TASA_PASARELA, 0)
                elif f["tipo"] == "CONTRACARGO":
                    com = Decimal(CARGO_CONTRACARGO)
                else:
                    com = Decimal(0)
                iva = redondear(com * IVA, 0)
                neto = bruto - com - iva
                total += int(neto)
                base = {"id_liquidacion": id_liq, "fecha_liquidacion": fl.isoformat(),
                        "ref_transaccion": f["ref"], "fecha_transaccion": local_naive(f["t"]),
                        "tipo_operacion": f["tipo"], "moneda_original": f["moneda"],
                        "monto_original": fmt_monto(f["monto"], f["moneda"]),
                        "tipo_cambio": str(f["tc"]) if f["moneda"] != "CLP" else "",
                        "monto_bruto_clp": str(int(bruto))}
                if nuevo:
                    base.update({"monto_liquidado": str(int(neto)), "comision_pasarela": str(int(com)),
                                 "iva_comision": str(int(iva))})
                else:
                    base.update({"comision_pasarela": str(int(com + iva)), "monto_neto": str(int(neto))})
                filas.append(base)
            if nuevo and fl == self.fecha_cambio_esquema:
                self.anotar("cambio_esquema", f"pasarela/liquidacion_{fl}.csv", fl.isoformat(),
                            "monto_neto->monto_liquidado; comision separada de iva_comision; orden de columnas")
            self.escribir_csv(f"pasarela/liquidacion_{fl.isoformat()}.csv", filas)
            deposito = total
            if fl == self.dia_retencion:
                ret = int(redondear(Decimal(total) * Decimal("0.05"), 0))
                deposito -= ret
                self.anotar("retencion_no_informada", f"banco ({fl})", id_liq, str(ret))
            self.banco[fl].append((f"ABONO PASARELA {id_liq}", id_liq, 0 if deposito >= 0 else -deposito,
                                   deposito if deposito >= 0 else 0))

    # ----------------------------------------------------------------- dispersiones
    def dispersar(self) -> None:
        pendiente: dict[str, Decimal] = defaultdict(Decimal)
        por_fecha = defaultdict(list)
        for (cid, dl), v in self.devengos.items():
            por_fecha[dl].append((cid, v))
        comercios = {c.id: c for c in self.comercios}
        d = self.desde
        fechas_dev = sorted(por_fecha)
        idx = 0
        while d <= self.hasta:
            while idx < len(fechas_dev) and fechas_dev[idx] < d:
                for cid, v in por_fecha[fechas_dev[idx]]:
                    pendiente[cid] += v
                idx += 1
            if es_habil(d):
                n_disp = 0
                for cid in sorted(pendiente):
                    monto = pendiente[cid]
                    if monto <= 0:
                        continue
                    t = datetime.combine(d, time(10, self.rng.randrange(60), self.rng.randrange(60)), TZ_LOCAL)
                    did, ref = self.nuevo_id("MOV-"), self.nuevo_id("DSP-", 9)
                    self.emitir(self.fila_ops(id_movimiento=did, tipo="DISPERSION", id_comercio=cid,
                                              medio="TRANSFERENCIA", monto=monto, referencia_externa=ref,
                                              creado_en=t, actualizado_en=t))
                    rut = fmt_rut(comercios[cid].rut_cuerpo)
                    self.banco[d].append((f"TRANSF A {rut}", ref, int(monto), 0))
                    if self.defecto(0.3):
                        self.banco[sig_habil(d)].append((f"DEVOLUCION TRANSF RECHAZADA {rut}", ref, 0, int(monto)))
                        self.anotar("dispersion_rebotada", f"banco ({sig_habil(d)})", ref, did)
                    pendiente[cid] = Decimal(0)
                    n_disp += 1
                if n_disp:
                    cargo = n_disp * COMISION_TRANSF_BANCO
                    self.banco[d].append(("COMISION TRANSFERENCIAS", "", int(cargo + redondear(cargo * IVA, 0)), 0))
                primer_habil_mes = not any(es_habil(d.replace(day=k)) for k in range(1, d.day))
                if primer_habil_mes:
                    self.banco[d].append(("COMISION MANTENCION CTA CTE", "", COMISION_MANTENCION_BANCO, 0))
            d += timedelta(days=1)

    # ----------------------------------------------------------------- escritura
    def escribir_csv(self, rel: str, filas: list[dict], **kw) -> None:
        ruta = self.salida / rel
        ruta.parent.mkdir(parents=True, exist_ok=True)
        if not filas:
            ruta.write_text("", encoding="utf-8")
            return
        with ruta.open("w", newline="", encoding=kw.get("encoding", "utf-8")) as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0].keys()), delimiter=kw.get("delimiter", ","))
            w.writeheader()
            w.writerows(filas)

    def escribir_ops(self) -> None:
        por_dia: dict[date, list] = defaultdict(list)
        for v in self.versiones_ops:
            d = v["actualizado_en"].astimezone(UTC).date()
            if self.defecto(0.8):
                d += timedelta(days=self.rd.choice([1, 1, 2]))
                self.anotar("registro_tardio", f"sistema_operativo/movimientos_{d}.csv", v["id_movimiento"])
            fila = dict(v)
            fila["monto"] = fmt_monto(v["monto"], v["moneda"])
            fila["creado_en"], fila["actualizado_en"] = iso_utc(v["creado_en"]), iso_utc(v["actualizado_en"])
            if self.defecto(0.4):
                fila["moneda"] = ""
                self.anotar("nulo_moneda", "sistema_operativo", v["id_movimiento"])
            if v["tipo"] == "PAGO" and v["medio"] == "TARJETA" and self.defecto(0.3):
                fila["referencia_externa"] = ""
                self.anotar("nulo_referencia", "sistema_operativo", v["id_movimiento"])
            if v["tipo"] == "COMISION" and self.defecto(0.2):
                fila["id_comercio"] = ""
                self.anotar("nulo_comercio", "sistema_operativo", v["id_movimiento"])
            por_dia[d].append(fila)
            if self.defecto(0.7):
                por_dia[d].append(dict(fila))
                self.anotar("duplicado", f"sistema_operativo/movimientos_{d}.csv", v["id_movimiento"])
        d = self.desde
        while d <= self.hasta:
            filas = sorted(por_dia.get(d, []), key=lambda f: f["actualizado_en"])
            self.escribir_csv(f"sistema_operativo/movimientos_{d.isoformat()}.csv", filas)
            if d == self.dia_reenvio:
                extra = filas + sorted(por_dia.get(d + timedelta(days=1), []), key=lambda f: f["actualizado_en"])[:5]
                self.escribir_csv(f"sistema_operativo/movimientos_{d.isoformat()}_reenvio.csv", extra)
                self.anotar("archivo_reenviado", f"sistema_operativo/movimientos_{d}_reenvio.csv", d.isoformat())
            d += timedelta(days=1)

    def escribir_banco(self) -> None:
        saldo = SALDO_INICIAL_BANCO
        acumulado: list[dict] = []
        d = self.desde
        while d <= self.hasta:
            if es_habil(d):
                for glosa, doc, cargo, abono in self.banco.get(d, []):
                    saldo += abono - cargo
                    acumulado.append({"Fecha": d.strftime("%d/%m/%Y"), "Fecha Valor": d.strftime("%d/%m/%Y"),
                                      "Descripción": glosa, "N° Documento": doc, "Cargos": fmt_banco(cargo),
                                      "Abonos": fmt_banco(abono), "Saldo": fmt_banco(saldo)})
                if d == self.dia_sin_extracto:
                    self.anotar("archivo_faltante", f"banco/extracto_{d:%Y%m%d}.csv", d.isoformat(),
                                "sus movimientos vienen en el extracto del día hábil siguiente")
                else:
                    self.escribir_csv(f"banco/extracto_{d:%Y%m%d}.csv", acumulado, delimiter=";", encoding="latin-1")
                    acumulado = []
            d += timedelta(days=1)

    def escribir_maestros(self) -> None:
        cuentas = [
            ("1101", "Banco cuenta corriente", "ACTIVO", "DEUDORA", "Dinero disponible en la cuenta corriente de la empresa."),
            ("1102", "Cuentas por cobrar pasarela", "ACTIVO", "DEUDORA", "Pagos con tarjeta aprobados que la pasarela aún no deposita."),
            ("1103", "Fondos por confirmar", "ACTIVO", "DEUDORA", "Transferencias informadas por clientes que aún no aparecen en el banco."),
            ("1104", "IVA crédito fiscal", "ACTIVO", "DEUDORA", "IVA pagado en comisiones de proveedores (pasarela, banco)."),
            ("2101", "Saldos por pagar a comercios", "PASIVO", "ACREEDORA", "Dinero recaudado que pertenece a los comercios y está pendiente de dispersión."),
            ("2102", "IVA débito fiscal", "PASIVO", "ACREEDORA", "IVA incluido en las comisiones cobradas a comercios."),
            ("2103", "Reembolsos por pagar", "PASIVO", "ACREEDORA", "Devoluciones aprobadas a compradores aún no ejecutadas."),
            ("3101", "Capital", "PATRIMONIO", "ACREEDORA", "Aportes de los socios."),
            ("4101", "Ingresos por comisiones", "INGRESO", "ACREEDORA", "Comisión neta de IVA cobrada a los comercios."),
            ("4102", "Diferencia de cambio (ganancia)", "INGRESO", "ACREEDORA", "Ganancia por conversión de moneda extranjera."),
            ("5101", "Gasto comisiones pasarela", "GASTO", "DEUDORA", "Comisión neta cobrada por la pasarela de pago."),
            ("5102", "Gasto comisiones bancarias", "GASTO", "DEUDORA", "Cargos del banco por mantención y transferencias."),
            ("5103", "Pérdida por contracargos", "GASTO", "DEUDORA", "Montos y cargos por desconocimiento de compras con tarjeta."),
            ("5104", "Diferencia de cambio (pérdida)", "GASTO", "DEUDORA", "Pérdida por conversión de moneda extranjera."),
            ("5105", "Diferencias de conciliación", "GASTO", "DEUDORA", "Diferencias menores aprobadas por contabilidad."),
        ]
        self.escribir_csv("maestros/plan_cuentas.csv", [
            {"codigo_cuenta": c, "nombre": n, "tipo": t, "naturaleza": na, "descripcion": de}
            for c, n, t, na, de in cuentas])
        self.escribir_csv("maestros/tipo_cambio.csv", [
            {"fecha": d.isoformat(), "moneda": "USD", "valor_clp": str(v)}
            for d, v in sorted(self.tc.items()) if self.desde - timedelta(days=7) <= d <= self.hasta])
        anios = range(self.desde.year, self.hasta.year + 1)
        self.escribir_csv("maestros/feriados.csv", [
            {"fecha": f"{y}-{mmdd}", "descripcion": "Feriado bancario"} for y in anios for mmdd in FERIADOS_MMDD])

    # ----------------------------------------------------------------- orquestación
    def correr(self) -> dict:
        self.crear_tipo_cambio()
        self.crear_comercios()
        d = self.desde
        while d <= self.hasta:
            self.simular_dia(d)
            self.foto_comercios(d)
            d += timedelta(days=1)
        self.dispersar()
        self.escribir_pasarela()
        self.escribir_ops()
        self.escribir_banco()
        self.escribir_maestros()
        manifiesto = {
            "generado_con": {"semilla": self.a.semilla, "desde": self.desde.isoformat(), "dias": self.a.dias,
                             "movs_por_dia": self.a.movs_por_dia, "pct_defectos": self.a.pct_defectos,
                             "escala": self.a.escala},
            "archivos": sorted(str(p.relative_to(self.salida)) for p in self.salida.rglob("*.csv")),
        }
        (self.salida / "manifiesto.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")
        if self.a.registro_revision:
            ruta = Path(self.a.registro_revision)
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with ruta.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["tipo", "archivo", "clave", "detalle"])
                w.writeheader()
                w.writerows(self.registro)
        return manifiesto


def parse_args(argv=None) -> argparse.Namespace:
    env = os.environ.get
    p = argparse.ArgumentParser(description="Genera los archivos sintéticos del caso Libro Mayor y Conciliación.")
    p.add_argument("--salida", default=env("GEN_SALIDA", "../data"), help="Carpeta de salida (se sobrescriben los archivos)")
    p.add_argument("--semilla", type=int, default=int(env("GEN_SEMILLA", "42")))
    p.add_argument("--desde", type=date.fromisoformat, default=date.fromisoformat(env("GEN_DESDE", "2026-10-01")),
                   help="Primer día simulado (AAAA-MM-DD)")
    p.add_argument("--dias", type=int, default=int(env("GEN_DIAS", "30")), help="Cantidad de días simulados")
    p.add_argument("--movs-por-dia", type=int, default=int(env("GEN_MOVS_POR_DIA", "300")),
                   help="Pagos por día antes de escalar")
    p.add_argument("--pct-defectos", type=float, default=float(env("GEN_PCT_DEFECTOS", "3")),
                   help="Porcentaje base de imperfecciones; 0 genera datos limpios")
    p.add_argument("--escala", type=float, default=float(env("GEN_ESCALA", "1")),
                   help="Factor xN de volumen (pagos por día y cantidad de comercios)")
    p.add_argument("--registro-revision", default=env("GEN_REGISTRO_REVISION", ""),
                   help="Uso interno de revisión: ruta de un CSV con el detalle de lo inyectado")
    a = p.parse_args(argv)
    if a.dias < 1 or a.movs_por_dia < 1 or a.escala <= 0 or not 0 <= a.pct_defectos <= 50:
        p.error("parámetros fuera de rango")
    return a


def main(argv=None) -> None:
    a = parse_args(argv)
    salida = Path(a.salida)
    for sub in ("sistema_operativo", "pasarela", "banco", "maestros"):
        for f in (salida / sub).rglob("*.csv") if (salida / sub).exists() else []:
            f.unlink()
    m = Generador(a).correr()
    print(f"Generados {len(m['archivos'])} archivos en {salida.resolve()}")


if __name__ == "__main__":
    main()

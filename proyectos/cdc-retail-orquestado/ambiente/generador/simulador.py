#!/usr/bin/env python3
"""Simulador de tráfico transaccional para la tienda en línea sintética.

Subcomandos:
  init   carga inicial (volumen = base x SIM_SCALE)
  run    tráfico continuo: inserts, updates y deletes a SIM_EPS transacciones/s

Todo el azar sale de random.Random(SIM_SEED): misma semilla + mismo estado de la
base => misma secuencia de operaciones. Los datos son 100% sintéticos.
"""
import argparse
import datetime as dt
import os
import random
import sys
import time

import psycopg2
from psycopg2.extras import execute_values

NOMBRES = ["Ana", "Luis", "María", "Carlos", "Sofía", "Jorge", "Lucía", "Pedro", "Valeria",
           "Diego", "Camila", "Andrés", "Daniela", "Mateo", "Paula", "Ricardo", "Elena", "Tomás"]
APELLIDOS = ["García", "López", "Martínez", "Rodríguez", "Hernández", "Pérez", "Gómez", "Torres",
             "Ramírez", "Flores", "Castro", "Vargas", "Rojas", "Mendoza", "Silva", "Cruz"]
CIUDADES = ["CDMX", "Guadalajara", "Monterrey", "Puebla", "Querétaro", "Mérida", "Tijuana", "León"]
CATEGORIAS = ["Electrónica", "Hogar", "Deportes", "Moda", "Juguetes", "Libros", "Belleza"]
ADJ = ["Pro", "Lite", "Max", "Plus", "Eco", "Smart", "Classic", "Ultra"]
COSAS = ["Audífonos", "Lámpara", "Mochila", "Botella", "Teclado", "Cafetera", "Tenis", "Reloj",
         "Cojín", "Balón", "Libreta", "Cargador", "Bocina", "Sartén"]
METODOS = ["tarjeta", "transferencia", "efectivo_contra_entrega", "billetera"]
FLUJO = ["creado", "pagado", "enviado", "entregado"]


def env(name, default):
    return os.environ.get(name, default)


def conectar():
    return psycopg2.connect(
        host=env("SIM_DB_HOST", "localhost"), port=int(env("SIM_DB_PORT", "5432")),
        dbname=env("SIM_DB_NAME", "tienda_db"), user=env("SIM_DB_USER", "app_tienda"),
        password=env("SIM_DB_PASSWORD", ""))


def ahora():
    return dt.datetime.now(dt.timezone.utc)


class Sim:
    def __init__(self, conn, rng, args):
        self.conn, self.rng, self.a = conn, rng, args
        self.p = args.defect_pct / 100.0
        self.clientes, self.productos, self.pedidos = [], [], []
        self.tiene_segmento = False
        self.ops = 0

    # ---- utilidades -------------------------------------------------------
    def defecto(self):
        return self.rng.random() < self.p

    def nombre(self):
        return f"{self.rng.choice(NOMBRES)} {self.rng.choice(APELLIDOS)}"

    def email_para(self, nombre, n):
        base = nombre.lower().replace(" ", ".")
        for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
            base = base.replace(a, b)
        return f"{base}{n}@ejemplo.test"

    def fila_cliente(self, n, ts):
        nombre = self.nombre()
        email = self.email_para(nombre, n)
        tel = f"55{self.rng.randint(10000000, 99999999)}"
        ciudad = self.rng.choice(CIUDADES)
        if self.defecto():                      # nulos / vacíos
            campo = self.rng.choice(["email", "telefono", "ciudad"])
            if campo == "email":
                email = None
            elif campo == "telefono":
                tel = None
            else:
                ciudad = self.rng.choice([None, ""])
        return [nombre, email, tel, ciudad, "MX", ts, ts]

    # ---- carga inicial ----------------------------------------------------
    def init(self):
        s = self.a.scale
        base = dt.datetime.fromisoformat(self.a.base_date).replace(tzinfo=dt.timezone.utc)
        cur = self.conn.cursor()
        cur.execute("SELECT count(*) FROM tienda.clientes")
        if cur.fetchone()[0] > 0:
            print("La base ya tiene datos; init no hace nada.")
            return
        ts = lambda: base - dt.timedelta(minutes=self.rng.randint(0, 60 * 24 * 60))
        filas = [self.fila_cliente(i, ts()) for i in range(500 * s)]
        # duplicados de cliente: mismo email con variante de mayúsculas, otro PK
        extra = [list(f) for f in filas if f[1] and self.defecto()]
        for f in extra:
            f[1] = f[1].upper()
        execute_values(cur, "INSERT INTO tienda.clientes (nombre,email,telefono,ciudad,pais,creado_en,updated_at) VALUES %s",
                       filas + extra)
        prods = []
        for i in range(100 * s):
            nom = f"{self.rng.choice(COSAS)} {self.rng.choice(ADJ)}"
            prods.append([f"SKU-{i:06d}", nom, self.rng.choice(CATEGORIAS),
                          round(self.rng.uniform(49, 4999), 2), True, base])
        execute_values(cur, "INSERT INTO tienda.productos (sku,nombre,categoria,precio,activo,updated_at) VALUES %s", prods)
        cur.execute("SELECT producto_id FROM tienda.productos ORDER BY 1")
        self.productos = [r[0] for r in cur.fetchall()]
        execute_values(cur, "INSERT INTO tienda.inventario (producto_id,cantidad,updated_at) VALUES %s",
                       [(p, self.rng.randint(0, 500), base) for p in self.productos])
        cur.execute("SELECT cliente_id FROM tienda.clientes ORDER BY 1")
        self.clientes = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT producto_id, precio FROM tienda.productos ORDER BY 1")
        precios = dict(cur.fetchall())
        for _ in range(1500 * s):
            self._pedido(cur, ts(), historico=True, precios=precios)
        self.conn.commit()
        print(f"init ok: {len(self.clientes)} clientes, {len(self.productos)} productos, {1500 * s} pedidos")

    # ---- transacciones de negocio ----------------------------------------
    def _pedido(self, cur, ts, historico=False, precios=None):
        cli = self.rng.choice(self.clientes)
        estado = self.rng.choice(FLUJO) if historico else "creado"
        cur.execute("INSERT INTO tienda.pedidos (cliente_id,estado,total,creado_en,updated_at) "
                    "VALUES (%s,%s,0,%s,%s) RETURNING pedido_id", (cli, estado, ts, ts))
        pid = cur.fetchone()[0]
        total = 0
        for prod in self.rng.sample(self.productos, k=min(len(self.productos), self.rng.randint(1, 4))):
            if precios is None:
                cur.execute("SELECT precio FROM tienda.productos WHERE producto_id=%s", (prod,))
                row = cur.fetchone()
                if row is None:
                    continue
                precio = row[0]
            else:
                precio = precios[prod]
            cant = self.rng.randint(1, 3)
            total += float(precio) * cant
            cur.execute("INSERT INTO tienda.pedido_items (pedido_id,producto_id,cantidad,precio_unitario) "
                        "VALUES (%s,%s,%s,%s)", (pid, prod, cant, precio))
        total = round(total, 2)
        if self.defecto():                      # total que no cuadra con las partidas
            total = round(total * self.rng.choice([0.9, 1.1, 0]), 2)
        cur.execute("UPDATE tienda.pedidos SET total=%s WHERE pedido_id=%s", (total, pid))
        if estado != "creado":
            cur.execute("INSERT INTO tienda.pagos (pedido_id,metodo,monto,pagado_en) VALUES (%s,%s,%s,%s)",
                        (pid, self.rng.choice(METODOS), total, ts))
        self.pedidos.append([pid, estado])
        return pid

    def op_nuevo_pedido(self, cur):
        self._pedido(cur, ahora())

    def op_nuevo_cliente(self, cur):
        f = self.fila_cliente(self.rng.randint(10**6, 10**7), ahora())
        if self.defecto() and self.clientes:    # re-registro del mismo email, otro PK
            cur.execute("SELECT email FROM tienda.clientes WHERE cliente_id=%s",
                        (self.rng.choice(self.clientes),))
            r = cur.fetchone()
            if r and r[0]:
                f[1] = r[0].upper()
        cols = "nombre,email,telefono,ciudad,pais,creado_en,updated_at"
        vals = f
        if self.tiene_segmento:
            cols += ",segmento"
            vals = f + [self.rng.choice(["nuevo", "recurrente", "vip", None])]
        cur.execute(f"INSERT INTO tienda.clientes ({cols}) VALUES ({','.join(['%s'] * len(vals))}) RETURNING cliente_id", vals)
        self.clientes.append(cur.fetchone()[0])

    def _ts_update(self):
        if self.defecto():                      # updated_at atrasado => evento tardío / desordenado
            return ahora() - dt.timedelta(hours=self.rng.randint(1, 72))
        return ahora()

    def op_actualizar_cliente(self, cur):
        cid = self.rng.choice(self.clientes)
        if self.defecto():                      # update sin cambio real (repetido)
            cur.execute("UPDATE tienda.clientes SET ciudad=ciudad WHERE cliente_id=%s", (cid,))
            return
        cur.execute("UPDATE tienda.clientes SET ciudad=%s, updated_at=%s WHERE cliente_id=%s",
                    (self.rng.choice(CIUDADES), self._ts_update(), cid))

    def op_avanzar_pedido(self, cur):
        if not self.pedidos:
            return
        i = self.rng.randrange(len(self.pedidos))
        pid, estado = self.pedidos[i]
        if estado in ("entregado", "cancelado"):
            return
        if self.defecto():                      # salto de estado fuera de orden
            nuevo = "entregado"
        elif self.rng.random() < 0.08:
            nuevo = "cancelado"
        else:
            nuevo = FLUJO[FLUJO.index(estado) + 1]
        cur.execute("UPDATE tienda.pedidos SET estado=%s, updated_at=%s WHERE pedido_id=%s",
                    (nuevo, self._ts_update(), pid))
        if nuevo == "pagado":
            cur.execute("SELECT total FROM tienda.pedidos WHERE pedido_id=%s", (pid,))
            r = cur.fetchone()
            if r:
                cur.execute("INSERT INTO tienda.pagos (pedido_id,metodo,monto) VALUES (%s,%s,%s)",
                            (pid, self.rng.choice(METODOS), r[0]))
        self.pedidos[i][1] = nuevo

    def op_inventario(self, cur):
        cur.execute("UPDATE tienda.inventario SET cantidad=%s, updated_at=%s WHERE producto_id=%s",
                    (self.rng.randint(0, 500), ahora(), self.rng.choice(self.productos)))

    def op_precio(self, cur):
        cur.execute("UPDATE tienda.productos SET precio=%s, updated_at=%s WHERE producto_id=%s",
                    (round(self.rng.uniform(49, 4999), 2), self._ts_update(), self.rng.choice(self.productos)))

    def op_borrar_item(self, cur):
        if not self.pedidos:
            return
        pid = self.rng.choice(self.pedidos)[0]
        cur.execute("DELETE FROM tienda.pedido_items WHERE item_id = (SELECT item_id FROM tienda.pedido_items "
                    "WHERE pedido_id=%s ORDER BY item_id LIMIT 1)", (pid,))

    def op_borrar_cliente(self, cur):
        cur.execute("SELECT cliente_id FROM tienda.clientes c WHERE NOT EXISTS "
                    "(SELECT 1 FROM tienda.pedidos p WHERE p.cliente_id=c.cliente_id) LIMIT 20")
        libres = [r[0] for r in cur.fetchall()]
        if libres:
            cid = self.rng.choice(libres)
            cur.execute("DELETE FROM tienda.clientes WHERE cliente_id=%s", (cid,))
            self.clientes.remove(cid)

    def op_borrar_reinsertar_producto(self, cur):
        """Defecto: el mismo PK desaparece y reaparece (borrado + alta con mismo id)."""
        pid = self.rng.choice(self.productos)
        cur.execute("SELECT sku,nombre,categoria,precio FROM tienda.productos WHERE producto_id=%s", (pid,))
        r = cur.fetchone()
        cur.execute("SELECT 1 FROM tienda.pedido_items WHERE producto_id=%s LIMIT 1", (pid,))
        if r is None or cur.fetchone():
            return
        cur.execute("DELETE FROM tienda.productos WHERE producto_id=%s", (pid,))
        cur.execute("INSERT INTO tienda.productos (producto_id,sku,nombre,categoria,precio) VALUES (%s,%s,%s,%s,%s)", (pid, *r))
        cur.execute("INSERT INTO tienda.inventario (producto_id,cantidad) VALUES (%s,%s)", (pid, self.rng.randint(0, 500)))

    OPS = [("op_nuevo_pedido", 35), ("op_avanzar_pedido", 25), ("op_inventario", 10),
           ("op_nuevo_cliente", 8), ("op_actualizar_cliente", 8), ("op_precio", 4),
           ("op_borrar_item", 3), ("op_borrar_cliente", 3)]

    def una_transaccion(self):
        if self.defecto() and self.rng.random() < 0.05:
            op = "op_borrar_reinsertar_producto"
        else:
            op = self.rng.choices([o for o, _ in self.OPS], [w for _, w in self.OPS])[0]
        cur = self.conn.cursor()
        try:
            getattr(self, op)(cur)
            self.conn.commit()
        except psycopg2.Error as e:             # el simulador no debe morir por una colisión de datos
            self.conn.rollback()
            print(f"[aviso] {op} falló y se descartó: {e.pgerror.strip() if e.pgerror else e}", file=sys.stderr)
        self.ops += 1

    # ---- cambios de esquema ----------------------------------------------
    def cambios_esquema(self):
        pendientes = self.a.schema_changes
        if pendientes and self.ops >= pendientes[0]:
            n = pendientes.pop(0)
            cur = self.conn.cursor()
            if not self.tiene_segmento and not getattr(self, "_c1", False):
                cur.execute("ALTER TABLE tienda.clientes ADD COLUMN segmento TEXT")
                self.tiene_segmento = self._c1 = True
                print(f"[esquema] op {n}: clientes + segmento")
            else:
                cur.execute("ALTER TABLE tienda.productos ALTER COLUMN precio TYPE NUMERIC(12,2)")
                print(f"[esquema] op {n}: productos.precio NUMERIC(12,2)")
            self.conn.commit()

    # ---- bucle principal --------------------------------------------------
    def run(self):
        cur = self.conn.cursor()
        cur.execute("SELECT cliente_id FROM tienda.clientes ORDER BY 1")
        self.clientes = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT producto_id FROM tienda.productos ORDER BY 1")
        self.productos = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT pedido_id, estado FROM tienda.pedidos ORDER BY 1")
        self.pedidos = [list(r) for r in cur.fetchall()]
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema='tienda' "
                    "AND table_name='clientes' AND column_name='segmento'")
        self.tiene_segmento = cur.fetchone() is not None
        if not self.clientes or not self.productos:
            sys.exit("Base vacía: ejecuta primero `init`.")
        eps = self.a.eps * self.a.scale
        t0 = time.monotonic()
        siguiente = t0
        outage_hecho = False
        print(f"run: eps efectivo={eps}, duración={self.a.duration}s, semilla={self.a.seed}")
        while True:
            t = time.monotonic() - t0
            if self.a.duration and t >= self.a.duration:
                break
            if self.p > 0 and self.a.outage_at and not outage_hecho and t >= self.a.outage_at:
                outage_hecho = True
                print(f"[caída] fuente en silencio {self.a.outage_len}s; luego ráfaga acumulada")
                time.sleep(self.a.outage_len)
                for _ in range(int(eps * self.a.outage_len)):
                    self.una_transaccion()
                siguiente = time.monotonic()
                continue
            factor = 1
            if self.p > 0 and self.a.spike_every and (t % self.a.spike_every) < self.a.spike_len and t >= self.a.spike_every:
                factor = self.a.spike_factor
            self.cambios_esquema() if self.p > 0 else None
            self.una_transaccion()
            siguiente += 1.0 / (eps * factor)
            espera = siguiente - time.monotonic()
            if espera > 0:
                time.sleep(espera)
            if self.ops % 200 == 0:
                print(f"  {self.ops} transacciones ({t:.0f}s)")
        print(f"run terminado: {self.ops} transacciones")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("comando", choices=["init", "run"])
    ap.add_argument("--seed", type=int, default=int(env("SIM_SEED", "42")))
    ap.add_argument("--scale", type=int, default=int(env("SIM_SCALE", "1")), help="factor xN de volumen y tasa")
    ap.add_argument("--eps", type=float, default=float(env("SIM_EPS", "5")), help="transacciones por segundo")
    ap.add_argument("--duration", type=float, default=float(env("SIM_DURATION_S", "120")), help="0 = infinito")
    ap.add_argument("--defect-pct", type=float, default=float(env("SIM_DEFECT_PCT", "5")))
    ap.add_argument("--schema-changes", default=env("SIM_SCHEMA_CHANGE_AT", "500,1500"),
                    help="ops acumuladas donde ocurre cada cambio de esquema; vacío = ninguno")
    ap.add_argument("--spike-every", type=float, default=float(env("SIM_SPIKE_EVERY_S", "60")))
    ap.add_argument("--spike-factor", type=float, default=float(env("SIM_SPIKE_FACTOR", "10")))
    ap.add_argument("--spike-len", type=float, default=float(env("SIM_SPIKE_LEN_S", "8")))
    ap.add_argument("--outage-at", type=float, default=float(env("SIM_OUTAGE_AT_S", "0")))
    ap.add_argument("--outage-len", type=float, default=float(env("SIM_OUTAGE_LEN_S", "20")))
    ap.add_argument("--base-date", default=env("SIM_BASE_DATE", "2026-09-01"))
    a = ap.parse_args()
    a.schema_changes = [int(x) for x in a.schema_changes.split(",") if x.strip()]
    sim = Sim(conectar(), random.Random(a.seed), a)
    sim.init() if a.comando == "init" else sim.run()


if __name__ == "__main__":
    main()

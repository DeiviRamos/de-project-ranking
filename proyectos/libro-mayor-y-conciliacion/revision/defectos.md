# Defectos inyectados (uso interno de evaluación)

Todo sale de `ambiente/generador/generar.py`. Hay dos generadores aleatorios:
- `rng = Random(GEN_SEMILLA)`: flujo de negocio (pagos, montos, horarios, planes).
- `rd = Random(GEN_SEMILLA + 10007)`: decisiones de imperfección y fechas de los defectos estructurales.

`p = GEN_PCT_DEFECTOS / 100` (default 3 → p = 0,03). Cada defecto por fila se activa con probabilidad `p × factor`. Los **estructurales** (archivo faltante, reenvío, pico, cambio de esquema, retención, transacción fantasma) solo existen si `GEN_PCT_DEFECTOS > 0`. Con `--pct-defectos 0` el registro queda vacío.

Para obtener la lista exacta de lo inyectado en una corrida (claves y archivos):

```bash
cd ambiente/generador
python3 generar.py --salida /tmp/revision-data --registro-revision /tmp/registro.csv
```

Con la semilla 42 y los parámetros por defecto, el registro trae unas 1.900 filas. Las fechas estructurales de esa corrida (las de `ambiente/data/` en el repo) están en la columna "semilla 42".

## Defectos por fila

| # | Defecto (`tipo` en el registro) | Dónde aparece | Cómo se genera | Señal que debería detectar un pipeline bien hecho |
|---|---|---|---|---|
| 1 | `duplicado` (operacional) | `sistema_operativo/movimientos_*.csv`: fila idéntica repetida en el mismo archivo | `p × 0.7` por versión | Unicidad por (`id_movimiento`, `actualizado_en`) antes de cargar; conteo de duplicados descartados en el log |
| 2 | `registro_tardio` | Una versión del movimiento llega en el archivo de 1 o 2 días después de su `actualizado_en` | `p × 0.8` por versión | No usar el nombre del archivo como fecha del hecho; carga incremental que acepta llegadas tardías; reproceso de días anteriores sin duplicar |
| 3 | `nulo_moneda` | `moneda` vacía en `sistema_operativo` | `p × 0.4` | Test not_null; regla explícita (inferir de la referencia/pasarela o enviar a cuarentena), no asumir CLP en silencio |
| 4 | `nulo_referencia` | `referencia_externa` vacía en pagos con tarjeta | `p × 0.3` | Pago aprobado sin forma directa de cruzarlo con la pasarela: conciliación por monto + fecha + comercio, o partida abierta explicada |
| 5 | `nulo_comercio` | `id_comercio` vacío en comisiones | `p × 0.2` | Recuperarlo desde el `PAGO` de `id_movimiento_origen`; test de integridad referencial |
| 6 | `comision_tasa_desactualizada` | Comisión calculada con la tasa del plan **anterior** de un comercio que cambió de plan | `p × 3` sobre aprobaciones de comercios con cambio de plan | Recalcular la comisión esperada con la tasa vigente al momento del pago (requiere historia del maestro: SCD2/snapshot) y reportar la diferencia |
| 7 | `reembolso_mayor_al_pago` | Reembolso con monto 1,5 veces el pago original | `p × 1.5` sobre reembolsos | Test: suma de reembolsos de un pago ≤ monto del pago |
| 8 | `reembolso_origen_inexistente` | `id_movimiento_origen` apunta a un pago que no existe | `p × 1.0` sobre reembolsos (excluyente con el 7) | Integridad referencial; el reembolso no se pierde: queda en cuarentena o partida abierta |
| 9 | `abono_sin_referencia` | Abono de transferencia en el banco con `N° Documento` vacío | `p × 0.6` sobre transferencias aprobadas | Conciliación difusa (monto exacto + ventana de fechas hábiles); medir cuántas se resuelven así |
| 10 | `abono_sin_pago_aprobado` | Llega al banco una transferencia que el sistema marcó `RECHAZADO` | `p × 0.3` sobre transferencias rechazadas | Abono bancario sin contrapartida: alerta, no se fuerza a cuadrar |
| 11 | `captura_no_liquidada` | Captura aprobada que la pasarela nunca liquida | `p × 0.5` sobre capturas | Partida abierta en cuentas por cobrar pasarela con antigüedad creciente; alerta pasado el plazo esperado (T+2 hábil) |
| 12 | `diferencia_redondeo` | `monto_bruto_clp` de la pasarela difiere en ±1 CLP del sistema | `p × 0.4` sobre operaciones liquidadas | Tolerancia explícita y documentada; se contabiliza en "Diferencias de conciliación", no se ignora en silencio |
| 13 | `liquidacion_duplicada` | La misma captura aparece en dos liquidaciones (día hábil siguiente) | `p × 0.15` sobre capturas | Unicidad de `ref_transaccion` por tipo de operación entre liquidaciones; cobro doble detectado |
| 14 | `contracargo` | Fila `CONTRACARGO` negativa, 3 días hábiles después, con cargo fijo de 15.000 + IVA; no existe en el sistema operativo | `p × 0.1` sobre capturas | Movimiento externo sin origen interno: se contabiliza (pérdida por contracargos) y se alerta |
| 15 | `dispersion_rebotada` | Transferencia a comercio que el banco devuelve al día hábil siguiente ("DEVOLUCION TRANSF RECHAZADA"); el sistema no se entera | `p × 0.3` sobre dispersiones | El pasivo con el comercio vuelve a quedar abierto; alerta a tesorería |
| 16 | `rut_formato_distinto` | RUT sin puntos en algunas fotos del maestro de comercios | `p × 0.5` por fila de foto | Normalizar el RUT; el cambio de formato no debe crear una versión nueva en la historia del comercio |
| 17 | `duplicado` (comercios) | Fila repetida en una foto del maestro | `p × 0.2` por fila de foto | Unicidad de `id_comercio` por foto |

## Defectos estructurales

| # | Defecto | Semilla 42 | Cómo se genera | Señal esperada |
|---|---|---|---|---|
| 18 | `pico_volumen` (×5 pagos en un día) | 2026-10-02 | `rd.choice` sobre los días (excepto el primero) | El proceso termina dentro del SLA; métricas de volumen por día con alerta de anomalía |
| 19 | `cambio_esquema` en la pasarela: `monto_neto` → `monto_liquidado` (ahora neto de comisión **e IVA**), `comision_pasarela` pasa a ser neta y aparece `iva_comision`; cambia el orden de columnas | desde 2026-10-19 | `rd.choice` entre los primeros 3 días hábiles de la segunda mitad | La ingesta no se cae ni lee mal por posición; detecta el cambio y lo alerta; la semántica de la comisión se ajusta (antes con IVA incluido, después separado) |
| 20 | `archivo_faltante` (banco): no se emite el extracto de un día hábil; sus movimientos vienen en el siguiente, con su propia `Fecha` | 2026-10-26 (llega en el de 2026-10-27) | `rd.choice` sobre días hábiles (sin los 2 primeros ni los 2 últimos) | Control de frescura/completitud por calendario hábil; usar la `Fecha` de cada fila, no la del archivo; el proceso del día no se cae |
| 21 | `archivo_faltante` (comercios): falta la foto de un día | 2026-10-20 | `rd.choice` | La historia del comercio no se corta ni se "cierra" ese día |
| 22 | `archivo_reenviado`: `movimientos_D_reenvio.csv` con todo lo del día D más 5 filas del día siguiente | D = 2026-10-15 | `rd.choice` | Carga idempotente: el reenvío no duplica; las 5 filas extra se integran sin romper el día siguiente |
| 23 | `retencion_no_informada`: el depósito de una liquidación es 5 % menor que la suma del archivo | LIQ-20261009 (338.467 CLP) | `rd.choice` sobre días hábiles | Total del archivo de la pasarela ≠ abono en el banco: alerta de descuadre a nivel de liquidación |
| 24 | `transaccion_fantasma`: captura en la pasarela con una `PSR-` que no existe en el sistema | ~60 % de las liquidaciones, 1 por archivo (10 con semilla 42) | `rd.random() < 0.6` por archivo | Operación externa sin origen interno: no se contabiliza como pago de un comercio; alerta |

## Trampas del dominio que no son defectos (y que también se evalúan)

- **Fecha local vs UTC:** el sistema exporta por día UTC; el negocio cierra por día de Santiago (UTC−3 en el período). Un pago a las 22:30 de Santiago cae en el archivo del día siguiente.
- **Pendientes que se resuelven después:** un pago `PENDIENTE` aparece de nuevo con su estado final (hasta 30 h después). Algunos quedan pendientes al cierre del período.
- **Calendario hábil:** sin extracto ni liquidación los fines de semana y feriados (`maestros/feriados.csv`: en el período caen el lunes 12/10 y el sábado 31/10). El tipo de cambio oficial tampoco se publica esos días.
- **Plazos de liquidación:** captura liquidada a T+1 hábil (10 % a T+2). Al final del período quedan capturas en tránsito, lo que es legítimo: no son descuadres.
- **Comisiones:** la comisión al comercio viene con IVA incluido (hay que separar ingreso e IVA débito). La comisión de la pasarela, antes del cambio de esquema, incluye IVA; después, no.
- **USD:** la pasarela convierte con su propio tipo de cambio (oficial × 0,985). Las dispersiones al comercio usan el oficial del día de la operación. La diferencia es diferencia de cambio, no un descuadre.
- **Gastos bancarios sin origen interno:** "COMISION TRANSFERENCIAS" (300 CLP + IVA por dispersión, diario) y "COMISION MANTENCION CTA CTE" (25.000 el primer día hábil del mes).
- **Reembolsos parciales** (30 % de los reembolsos) y comisión no devuelta en el reembolso (regla que el brief deja abierta).
- **Comercios suspendidos** no reciben pagos nuevos, pero siguen recibiendo dispersiones y reembolsos de lo anterior.
- **Saldo del banco:** la columna `Saldo` permite validar la continuidad del extracto (saldo inicial de la simulación: 150.000.000 CLP).

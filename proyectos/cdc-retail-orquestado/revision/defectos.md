# Defectos inyectados (uso interno de evaluación)

Todos salen de `random.Random(SIM_SEED)` en `ambiente/generador/simulador.py`; el porcentaje por operación es `SIM_DEFECT_PCT` (default 5). Los estructurales se activan solo si `SIM_DEFECT_PCT > 0`. Para reproducir: misma semilla, misma base inicial (`init` con igual semilla/escala).

| # | Defecto | Dónde | Cómo se genera | Señal que debe detectar un pipeline bien hecho |
|---|---|---|---|---|
| 1 | Clientes duplicados por email (otro PK, mayúsculas distintas) | `clientes` en `init` y `op_nuevo_cliente` | `SIM_DEFECT_PCT` | Test de unicidad de email normalizado; regla de deduplicación o marca en plata |
| 2 | Nulos y vacíos | `clientes.email/telefono/ciudad` (ciudad también `''`) | `SIM_DEFECT_PCT`, `init` y alta | Tests not_null/accepted con umbral; tratamiento explícito de `''` vs NULL |
| 3 | Total del pedido que no cuadra con sus partidas (x0.9, x1.1, 0) | `pedidos.total` en `_pedido` | `SIM_DEFECT_PCT` | Test de conciliación total vs suma de items; además hay desajuste legítimo por borrado de items |
| 4 | Eventos tardíos / desordenados | `updated_at` atrasado 1–72 h en updates de clientes, pedidos, productos | `_ts_update`, `SIM_DEFECT_PCT` | No usar `updated_at` como orden; ordenar por LSN/offset de origen; resolver con el último evento por posición en el log |
| 5 | UPDATE sin cambio real | `op_actualizar_cliente` (`SET ciudad=ciudad`) | `SIM_DEFECT_PCT` | Eventos con before = after; el modelo con historial no debe crear versión nueva |
| 6 | Saltos de estado fuera de orden | `pedidos.estado` → `entregado` directo | `op_avanzar_pedido` | Test de transiciones válidas del estado |
| 7 | Borrado y reinserción del mismo PK | `productos`/`inventario` | `op_borrar_reinsertar_producto` (≈0.25 % de ops con defecto) | Delete seguido de create con misma clave; no perder historia ni duplicar la versión vigente |
| 8 | Cambios de esquema | `clientes` + columna `segmento` (op 500); `productos.precio` a NUMERIC(12,2) (op 1500) | `SIM_SCHEMA_CHANGE_AT` | El pipeline no se cae ni descarta la columna nueva; el cambio queda visible/alertado |
| 9 | Picos de volumen | Toda la carga ×`SIM_SPIKE_FACTOR` durante `SIM_SPIKE_LEN_S` cada `SIM_SPIKE_EVERY_S` | Parámetros de pico | Lag del consumidor medido; sin pérdidas ni duplicados tras el pico |
| 10 | Caída de la fuente con ráfaga | Silencio `SIM_OUTAGE_LEN_S` desde `SIM_OUTAGE_AT_S`, luego transacciones acumuladas | Parámetros de caída (desactivado por defecto) | Detección de silencio (frescura); reproceso idempotente de la ráfaga |
| 11 | Deletes reales | Borrado de clientes sin pedidos, de partidas | Tráfico normal | Los deletes se reflejan (o se marcan) en las capas; no quedan filas fantasma |

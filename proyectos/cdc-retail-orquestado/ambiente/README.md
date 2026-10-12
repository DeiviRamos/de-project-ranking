# Ambiente — CDC Retail Orquestado (Fase 1)

Qué trae: Postgres transaccional (`postgres-fuente`) con el esquema `tienda` y replicación lógica habilitada, un Postgres vacío (`postgres-dwh`) como destino, un broker Redpanda (sin conectores ni consumidores) y un simulador de tráfico. Todo local, sin servicios externos ni de pago. Datos sintéticos.

Requisitos: Docker con Compose v2.

## Levantar (un comando tras configurar `.env`)
```bash
cd proyectos/cdc-retail-orquestado/ambiente
cp .env.example .env
docker compose up -d --build
```
Verifica que los tres servicios estén `healthy`:
```bash
docker compose ps
```

## Cargar datos iniciales y generar tráfico
```bash
docker compose run --rm simulador init
docker compose run --rm simulador run
```
`run` termina tras `SIM_DURATION_S` segundos (0 = infinito, detén con Ctrl+C).

## Acceso
```bash
# Fuente
docker compose exec postgres-fuente psql -U app_tienda -d tienda_db -c '\dt tienda.*'
# Destino vacío
docker compose exec postgres-dwh psql -U dwh_user -d dwh
# Broker
docker compose exec redpanda rpk cluster info
```
Desde el host: fuente `localhost:5432`, destino `localhost:5433`, Kafka `localhost:19092`. Dentro de la red de Compose el broker es `redpanda:9092`. Publicación de replicación: `cdc_publication`; rol: `CDC_USER` del `.env`.

## Controles del simulador
Por variable de entorno (en `.env`) o argumento (`docker compose run --rm simulador run --eps 20 --seed 7`).

| Variable | Argumento | Default | Efecto |
|---|---|---|---|
| SIM_SEED | --seed | 42 | Semilla; misma semilla y mismo estado inicial => misma secuencia de operaciones |
| SIM_SCALE | --scale | 1 | Factor xN: multiplica el volumen inicial (`init`) y la tasa de `run` |
| SIM_EPS | --eps | 5 | Transacciones por segundo (antes de escalar) |
| SIM_DURATION_S | --duration | 120 | Duración de `run` en segundos (0 = infinito) |
| SIM_DEFECT_PCT | --defect-pct | 5 | Porcentaje de operaciones con imperfecciones; 0 desactiva también las irregularidades estructurales |
| SIM_SCHEMA_CHANGE_AT | --schema-changes | 500,1500 | Transacciones acumuladas en las que ocurren cambios de esquema en la fuente (vacío = ninguno) |
| SIM_SPIKE_EVERY_S / _FACTOR / _LEN_S | --spike-* | 60 / 10 / 8 | Picos periódicos de tráfico |
| SIM_OUTAGE_AT_S / _LEN_S | --outage-* | 0 / 20 | Silencio de la fuente seguido de ráfaga (0 = desactivado) |
| SIM_BASE_DATE | --base-date | 2026-09-01 | Fecha de referencia del histórico inicial |

Reiniciar desde cero (borra volúmenes):
```bash
docker compose down -v
docker compose up -d --build
```

El simulador procesa transacciones de una sola conexión; tasas muy altas (> ~300/s) pueden no alcanzarse.

## Estado de verificación
Probado: el simulador (`init` y `run`) contra un Postgres 16 local, con DDL y cambios de esquema. **No probado** en esta entrega: `docker compose up`, el script `02_replicacion.sh`, Redpanda y el build de la imagen (no había daemon de Docker disponible).

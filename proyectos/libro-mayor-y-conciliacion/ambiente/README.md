# Ambiente: Libro Mayor y Conciliación

Qué trae:

- Un **Postgres 16 vacío** (`postgres`), que es tu base de trabajo. No trae esquema: lo diseñas tú.
- Los **archivos de las fuentes ya generados** en `data/` (30 días, unos 4 MB), montados en solo lectura dentro del contenedor en `/data`.
- Un **generador** (`generador/generar.py`) para regenerar los archivos con otra semilla, más días o más volumen.

Todo es local y sintético. No hay servicios externos ni de pago. El mismo ambiente sirve para las dos etapas: la v1 (Python + cron) y la v2 (dbt + orquestador) leen los mismos archivos y escriben en el mismo Postgres.

Requisitos: Docker con Compose v2. Para correr el generador sin Docker: Python 3.10 o superior.

## 1. Levantar (desde un clon limpio)

```bash
cd proyectos/libro-mayor-y-conciliacion/ambiente
cp .env.example .env
docker compose up -d
```

Después de copiar el `.env`, el ambiente se levanta con un solo comando: `docker compose up -d`. Cambia `POSTGRES_PASSWORD` en `.env` antes de usarlo en tu VPS.

Revisa que el servicio quede `healthy`:

```bash
docker compose ps
```

## 2. Conectarse

```bash
docker compose exec postgres psql -U finanzas -d contabilidad
```

Desde el host: `localhost:5432` (o el puerto que definas en `PG_PORT`), con el usuario, la clave y la base del `.env`.

Los archivos se ven dentro del contenedor:

```bash
docker compose exec postgres ls /data /data/banco
```

## 3. Las fuentes

Tienes que tratar `data/` como si cada carpeta fuera una entrega diaria de un sistema distinto. El detalle de cada campo está en [`diccionario-datos.md`](diccionario-datos.md).

| Carpeta | Quién la entrega | Archivo | Frecuencia |
|---|---|---|---|
| `sistema_operativo/` | Sistema propio de la fintech | `movimientos_AAAA-MM-DD.csv` | Diaria, todos los días |
| `pasarela/` | Pasarela de pago con tarjeta | `liquidacion_AAAA-MM-DD.csv` | Días hábiles |
| `banco/` | Banco (cuenta corriente) | `extracto_AAAAMMDD.csv` | Días hábiles |
| `maestros/comercios/` | Área comercial | `comercios_AAAA-MM-DD.csv` (foto completa) | Diaria |
| `maestros/` | Contabilidad / Tesorería | `plan_cuentas.csv`, `tipo_cambio.csv`, `feriados.csv` | Cuando cambian |

`data/manifiesto.json` registra con qué parámetros se generó la carpeta.

## 4. Regenerar los datos

### Con Docker

```bash
docker compose --profile generador run --rm generador
```

El generador lee los `GEN_*` del `.env`. Para cambiar un parámetro en una corrida puntual, pasa argumentos después del nombre del servicio (si das argumentos, incluye también `--salida /salida`):

```bash
docker compose --profile generador run --rm generador --salida /salida --semilla 7 --dias 60
```

### Sin Docker

```bash
cd generador
python3 generar.py --salida ../data
cd ..
```

**Ojo:** el generador borra y reescribe los CSV de la carpeta de salida. Para probar volumen, usa otra carpeta (ya está en el `.gitignore`) y no la subas al repo:

```bash
cd generador
python3 generar.py --salida ../data-grande --escala 10 --dias 60
cd ..
```

### Controles

Por variable de entorno (en `.env`) o por argumento. El argumento manda sobre la variable.

| Variable | Argumento | Default | Efecto |
|---|---|---|---|
| `GEN_SEMILLA` | `--semilla` | 42 | Semilla. Mismos parámetros y misma semilla generan archivos idénticos |
| `GEN_DESDE` | `--desde` | 2026-10-01 | Primer día simulado (AAAA-MM-DD) |
| `GEN_DIAS` | `--dias` | 30 | Días simulados |
| `GEN_MOVS_POR_DIA` | `--movs-por-dia` | 300 | Pagos por día, antes de escalar. Las comisiones, reembolsos y dispersiones se derivan de ellos |
| `GEN_PCT_DEFECTOS` | `--pct-defectos` | 3 | Porcentaje base de imperfecciones (0 a 50). Con 0 los datos salen limpios y sin irregularidades de entrega |
| `GEN_ESCALA` | `--escala` | 1 | Factor xN: multiplica los pagos por día y la cantidad de comercios |
| `GEN_SALIDA` | `--salida` | `../data` | Carpeta de salida |
| `GEN_REGISTRO_REVISION` | `--registro-revision` | (vacío) | Uso interno del proceso de revisión. Si quieres el desafío completo, no lo uses |

Referencia de volumen (medida en un portátil, sin Docker): el default genera cerca de 23 mil filas en `sistema_operativo/` en menos de 1 s; `--escala 10 --dias 10` genera unos 15 MB en unos 3 s.

## 5. Reiniciar desde cero

Borra la base (y su volumen) y vuelve a levantarla:

```bash
docker compose down -v
docker compose up -d
```

## Estado de verificación

- **Probado:** el generador con Python 3.11 (default, `--pct-defectos 0`, `--escala 10`, un solo día), su reproducibilidad con la misma semilla, la sintaxis del `docker-compose.yml` (`docker compose config`) y la carga de un archivo de cada fuente en un Postgres 16 local con `\copy`.
- **No probado:** `docker compose up`, el build de la imagen del generador ni el montaje de `/data`, porque no había un daemon de Docker en el entorno donde se armó el kit.

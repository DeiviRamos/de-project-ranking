#!/bin/bash
# Rol y publicación para replicación lógica (pgoutput). Se ejecuta una sola vez al crear el volumen.
set -euo pipefail
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<SQL
CREATE ROLE ${CDC_USER} WITH LOGIN REPLICATION PASSWORD '${CDC_PASSWORD}';
GRANT USAGE ON SCHEMA tienda TO ${CDC_USER};
GRANT SELECT ON ALL TABLES IN SCHEMA tienda TO ${CDC_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA tienda GRANT SELECT ON TABLES TO ${CDC_USER};
CREATE PUBLICATION cdc_publication FOR ALL TABLES;
SQL

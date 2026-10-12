# FICHA — CDC Retail Orquestado

- **Dominio:** Retail/e-commerce
- **Tipo de carga:** CDC (reto principal: evolución de esquema y calidad de datos)
- **Resumen:** Una tienda en línea simulada opera sobre una base transaccional (pedidos, clientes, inventario). El negocio necesita analítica casi en tiempo real sin consultar la base operativa. El proyecto captura los cambios de esa base, los transporta por un bus de eventos y los modela en capas medallón con esquema dimensional (incluyendo historial de cambios), todo probado y orquestado.
- **Stack:** Python, SQL, PostgreSQL, dbt, Docker, VPS, arquitectura medallón (dominados) + **Debezium (nuevo)**, **Redpanda (nuevo)**, **Dagster (nuevo)**, **GitHub Actions (nuevo)**, asset checks de Dagster (nuevo).
- **Huecos que cierra:** streaming, orquestación, testing de datos, CI/CD, git con ramas y PRs, modelado dimensional (SCD).
- **Pros:**
  - Cubre 6 de los 7 huecos prioritarios en un solo proyecto.
  - Extiende lo ya dominado (Postgres, dbt, medallón).
  - Todo corre en Docker a costo cero; existe un lab oficial de referencia.
- **Contras:**
  - Más de 3 herramientas nuevas; por eso se propone Fase 1.
  - Debezium requiere depurar replicación lógica de Postgres.
  - Sin volumen real: la escala se demuestra de forma sintética.
- **Puntajes (1-5):** Cierre de huecos 5 | Valor para portafolio 5 | Demanda 3.0 (Latam 3 / global 3) | Dificultad/aprendizaje 4 (sobre la Fase 1) | Reutilización del stack 5
- **Total:** 5×0.30 + 5×0.25 + 3.0×0.20 + 4×0.15 + 5×0.10 = 1.50 + 1.25 + 0.60 + 0.60 + 0.50 = **4.45**
- **Evidencia de demanda:**
  - Latam: ofertas remotas para Latam que piden dbt y orquestación con Airflow, p. ej. Muttdata "Data Engineer Senior DBT" (https://jobs.lever.co/muttdata/dd6fe048-650e-417f-8669-3afafa7a8c6b/apply, consultada 2026-10-07) y Ryzlabs (dbt + Airflow, publicada 2026-07-07: https://jobera.com/job/ryzlabs-data-engineer-61df6ce2/, consultada 2026-10-07). Kafka/streaming, Dagster y Debezium en Latam: **sin evidencia** concreta (una búsqueda solo indica que "varias" ofertas mencionan Kafka, sin dato). Por eso Latam = 3.
  - Latam (análisis previo, no re-verificado esta semana): 1,467 ofertas con CI/CD en 16.2% (https://bertonisolutions.com/blog/hiring-data-engineers-latam-2026, consultado 2026-10-06; fuente de terceros).
  - Global: un análisis de ofertas 2026 reporta Airflow en 48%, Kafka en 41% y dbt en 33% (https://blog.dataengineerthings.org/stop-chasing-every-new-data-tool-here-is-the-real-data-engineering-stack-for-2026-bb7dcb131070, consultado 2026-10-06; **fuente de terceros**, por eso global baja de 4 a 3). Otra guía indica que Airflow y Kafka suelen aparecer como "preferidos" más que requeridos (https://www.thirstysprout.com/post/data-engineering-skills-required, consultado 2026-10-06; fuente de terceros).
- **Desafío real que replica:** mantener sincronizadas bases heterogéneas capturando cambios del log de transacciones y, a la vez, poder reconstruir el estado completo de las tablas sin bloquear el origen. Fuente primaria (artículo de los autores de Netflix sobre DBLog, no leído en completo): https://arxiv.org/abs/2010.12597 (consultado 2026-10-07). Referencia técnica de implementación: https://docs.redpanda.com/labs/docker-compose/cdc-postgres-json.md
- **Fase 1 (3 semanas):** Postgres transaccional simulado → Debezium → Redpanda → capa bronce en Postgres; capa plata y oro con dbt (dimensión con historial de cambios); pruebas dbt; GitHub Actions con ramas y PRs que ejecutan lint y pruebas; documentación y diagrama de arquitectura desde la semana 1. Dagster y asset checks pasan a Fase 2 (semana 4+).

## Notas: fases siguientes (fuera del alcance de este kit)

- **Fase 2 (semana 4+):** orquestación con Dagster y asset checks sobre el pipeline de la Fase 1. El brief, el ambiente y el DoD de este kit cubren **solo la Fase 1**.

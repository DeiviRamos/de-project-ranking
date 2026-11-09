# Ranking vivo de proyectos

**Proyecto activo:** CDC Retail Orquestado

**Ejecución:** 2026-11-09 (Δ contra el ranking del 2026-10-07)

> Nota de método: las fechas de las fuentes son la fecha de consulta (2026-11-09) salvo que se indique otra. Esta semana el dominio www.uber.com no resolvió desde el entorno (debería permitirse en la configuración de red de la sesión); los enlaces primarios de Uber y Netflix siguen sin verificarse en contenido ni fecha. Las ofertas Latam se obtuvieron vía buscador y agregadores; no se confirmó que sigan abiertas.

## Top 5

| # | Proyecto | Dominio | Carga | Total | Δ |
|---|----------|---------|-------|-------|---|
| 1 | CDC Retail Orquestado | Retail/e-commerce | CDC | 4.45 | = |
| 2 | Telemetría de Flota en Vivo | Movilidad | Streaming | 3.85 | = |
| 3 | Torre de Control Logística (provisional: sin fuente primaria) | Logística | Consumo de API | 3.75 | = |
| 4 | Sensores Industriales en Series de Tiempo (provisional: sin fuente primaria) | IoT/industria | Streaming | 3.70 | = |
| 5 | Observatorio de Calidad Clínica | Salud | Batch | 3.50 | = |

Variedad: top 3 con dominios distintos (retail, movilidad, logística); 4 tipos de carga en el top 5 (CDC, streaming, API, batch). Solo 3 proyectos (#1, #2, #5) tienen fuente primaria; los otros dos completan el top 5 como provisionales.

## Ficha completa #1 — CDC Retail Orquestado

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

## Fichas resumidas #2–#5

**#2 Telemetría de Flota en Vivo** (Movilidad, streaming; reto: latencia). Feed de posiciones de vehículos (datos abiertos de transporte) por Redpanda, consumidores en Python y agregación por ventanas de tiempo y celdas geográficas en Postgres. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3: ofertas con Kafka/streaming en GetOnBoard y agregadores, ver abajo / global 3, solo fuentes de terceros) | dificultad 5 | reutilización 3 → **3.85**. Desafío real: agregar eventos de conductores y pasajeros por celda geográfica y ventana de un minuto en tiempo casi real, con suavizado espacial. Fuente primaria (Uber Engineering, sin leer en completo): https://www.uber.com/en-MY/blog/building-scalable-streaming-pipelines (consultado 2026-10-07).

**#3 Torre de Control Logística (provisional: sin fuente primaria)** (Logística, consumo de API; reto: modelado). Ingesta periódica de APIs abiertas de envíos/clima/tráfico, orquestada con Dagster, modelo dimensional con snapshots de dbt y pruebas. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 por ofertas dbt/Airflow citadas arriba / global 3, fuentes de terceros) | dificultad 3 | reutilización 5 → **3.75**. Desafío real: sin evidencia de blog primario específico; sigue pendiente.

**#4 Sensores Industriales en Series de Tiempo (provisional: sin fuente primaria)** (IoT/industria, streaming; reto: volumen). Sensores simulados por Redpanda hacia Postgres con particionado y retención, vistas agregadas. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 por ofertas con Kafka en tiempo real / global 3) | dificultad 4 | reutilización 3 → **3.70**. Desafío real: sin evidencia de blog primario; pendiente.

**#5 Observatorio de Calidad Clínica** (Salud, batch; reto: calidad de datos). Datos de salud abiertos o sintéticos con reglas de calidad por niveles (críticos vs. secundarios), pruebas dbt y CI que bloquea PRs. Puntajes: huecos 4 | portafolio 3 | demanda 3.0 (Latam 3 / global 3; calidad de datos en 43% de ofertas según https://www.thirstysprout.com/post/data-engineering-skills-required, fuente de terceros, consultada 2026-10-06) | dificultad 3 | reutilización 5 → **3.50**. Desafío real: clasificar datasets por niveles (tiers) con SLAs y checks estándar según criticidad. Fuente primaria (Uber Engineering, sin leer en completo): https://www.uber.com/blog/operational-excellence-data-quality/ (consultado 2026-10-07).

## Banca (#6–#10)

Sin re-puntuar a fondo esta semana: no hubo evidencia nueva que los afecte.

6. Libro Mayor y Conciliación — Finanzas (batch/CDC; modelado y evolución de esquema) — **3.45**
7. Medidores Inteligentes y Tarifas — Energía (batch; SQL avanzado, volumen) — **3.20**
8. CDR Telecom con Evolución de Esquema — Telecom (streaming/batch; evolución de esquema) — **3.05**
9. Monitor de Precios y Promociones — Retail/e-commerce (consumo de API; calidad de datos) — **2.75**
10. Demanda Energética con APIs Abiertas — Energía (consumo de API; modelado) — **2.70**

## Qué cambió esta semana y por qué

- Semana 2026-11-09: se encontró evidencia Latam concreta de streaming: Playbypoint "Data Engineer (Latam)" en GetOnBoard, con Kafka y Airflow, ya cerrada (https://www.getonbrd.com/jobs/data-science-analytics/data-engineer-remote-latam-playbypoint-remote, consultada 2026-11-09); 2BRAINS "Data Engineer Semi Senior" en GetOnBoard, con dbt deseable y tiempo real con Kafka o Kinesis (https://www.getonbrd.com/empleos/data-science-analytics/data-engineer-semi-senior-2brains-remote-72b9, consultada 2026-11-09); y un puesto senior remoto Latam con Airflow, dbt y Kafka/Kinesis en agregador (https://remotejobs.lat/es/job-offers/45660-senior-data-engineer, consultada 2026-11-09). Con ello Latam sube de 2 a 3 en #2 y #4 (Telemetría 3.75 → 3.85; Sensores 3.60 → 3.70). #1 mantiene Latam 3: Dagster y Debezium siguen "sin evidencia" en Latam. La oferta de Ryzlabs usa Snowflake; se traduce a Postgres.
- Global: un análisis de terceros de 6,877 ofertas (mayo 2026) y otro de Q1 2026 coinciden en que dbt y Airflow son los más frecuentes, Kafka se concentra en roles de streaming y Dagster crece en startups (https://dev.to/gnana_6392e836fd500a957dc/data-engineer-skills-companies-want-in-2026-6877-posting-analysis-44p9 y https://jobstrack.io/blog/roles/data-engineer, consultadas 2026-11-09; fuentes de terceros, sin cambio en puntajes globales).
- Buenas prácticas oficiales: la guía de asset checks de Dagster recomienda una propiedad por check y bloquear dependientes con blocking=True (https://docs.dagster.io/guides/test/asset-checks, consultada 2026-11-09); aplica a la Fase 2 de #1.
- Fuente primaria candidata sin asignar: DoorDash, sistema de eventos Iguazu con Kafka y Flink (https://doordash.engineering/2022/08/02/building-scalable-real-time-event-processing-with-kafka-and-flink/, consultada 2026-11-09; sin leer en completo). Ningún proyecto del pool la replica con fidelidad; no se asignó. Para IoT/industria no se halló blog primario de big tech (solo tutoriales de proveedores), y para logística la búsqueda tampoco arrojó uno específico.
- Sin cambios en el orden del top 5; la banca no se re-puntuó.
- Semana anterior (2026-10-07): se aplicó con más rigor la regla de fuentes de terceros: la demanda global pasó de 4 a 3 en todos los proyectos que solo la sustentaban con blogs de análisis. Esto bajó los totales (#1: 4.55 → 4.45).
- Se encontraron ofertas Latam concretas (Muttdata, Ryzlabs) para dbt y Airflow; sostienen Latam = 3 en #1, #3 y #5. Kafka/Dagster en Latam siguen "sin evidencia".
- Se añadieron fuentes primarias: #1 (DBLog de Netflix, artículo en arXiv, reemplaza el resumen de terceros), #2 (Uber, streaming geoespacial) y #5 (Uber, calidad de datos). Con ello Telemetría de Flota sube a #2 y Calidad Clínica queda con fuente primaria.
- Logística y Sensores siguen sin fuente primaria y se marcan provisionales; Calidad Clínica cae al #5 por score. Falta una fuente primaria para al menos dos proyectos más para cumplir el requisito del top 5.
- Se agregó la Fase 1 de #1 (exigida por tener más de 3 herramientas nuevas).
- Limitación: no se pudo abrir ningún blog de ingeniería; los enlaces primarios no están verificados en su contenido ni fecha. Pendiente para la próxima semana: verificarlos y buscar fuente primaria para Logística, Sensores y la banca.

## Proyectos previos

_(Sección fija: la edita el usuario. Aún vacía.)_

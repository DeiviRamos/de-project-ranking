# Ranking vivo de proyectos

**Proyecto activo:** CDC Retail Orquestado

**Ejecución:** 2026-10-26 (Δ contra el ranking del 2026-10-07)

> Nota de método: fechas de fuentes = fecha de consulta (2026-10-26). La búsqueda no devolvió ofertas de GetOnBoard ni LinkedIn Latam verificables; la evidencia Latam proviene de agregadores (Remotefront, SimplyHired MX) sin fecha de publicación. Los blogs de ingeniería se localizaron por buscador y no se leyeron completos. Se aplica la regla: sin evidencia Latam concreta, Latam ≤ 2.

## Top 5

| # | Proyecto | Dominio | Carga | Total | Δ |
|---|----------|---------|-------|-------|---|
| 1 | Telemetría de Flota en Vivo | Movilidad | Streaming | 3.75 | ▲1 |
| 2 | Torre de Control Logística (provisional: sin fuente primaria) | Logística | Consumo de API | 3.75 | ▲1 |
| 3 | Sensores Industriales en Series de Tiempo (provisional: sin fuente primaria) | IoT/industria | Streaming | 3.60 | ▲1 |
| 4 | Observatorio de Calidad Clínica | Salud | Batch | 3.50 | ▲1 |
| 5 | Libro Mayor y Conciliación | Finanzas | Batch/CDC | 3.35 | ▲1 |

Variedad: top 3 con dominios distintos (movilidad, logística, IoT); 4 tipos de carga (streaming, API, batch, CDC). Solo 3 proyectos (#1, #4, #5) tienen fuente primaria; los otros dos completan el top 5 como provisionales. Todos suben una posición porque "CDC Retail Orquestado" (proyecto activo) sale del pool.

## Ficha completa #1 — Telemetría de Flota en Vivo

- **Dominio:** Movilidad
- **Tipo de carga:** Streaming (reto principal: latencia)
- **Resumen:** Una operación de transporte necesita saber, casi en tiempo real, cuántos vehículos hay por zona y cómo evoluciona la oferta en la ciudad. El proyecto ingiere posiciones de vehículos (datos abiertos de transporte), las transporta por un bus de eventos y las agrega por ventana de tiempo y celda geográfica, sirviendo el resultado desde Postgres.
- **Stack:** Python, SQL, PostgreSQL, Docker, VPS (dominados) + **Redpanda (nuevo)**, **consumidores streaming en Python (nuevo)**, **GitHub Actions (nuevo)**. Dagster opcional en Fase 2 (nuevo).
- **Huecos que cierra:** streaming, testing de datos, CI/CD, git con ramas y PRs, SQL avanzado (funciones de ventana).
- **Pros:**
  - Ataca el hueco de streaming con una herramienta única (Redpanda).
  - Latencia medible: métrica concreta para el README y entrevistas.
  - Todo corre en Docker a costo cero.
- **Contras:**
  - No cubre orquestación ni modelado dimensional en Fase 1.
  - Demanda Latam de streaming con poca evidencia.
  - Depende de la calidad de un feed abierto o de un simulador.
- **Puntajes (1-5):** Cierre de huecos 4 | Valor para portafolio 4 | Demanda 2.5 (Latam 2 / global 3) | Dificultad/aprendizaje 5 | Reutilización del stack 3
- **Total:** 4×0.30 + 4×0.25 + 2.5×0.20 + 5×0.15 + 3×0.10 = 1.20 + 1.00 + 0.50 + 0.75 + 0.30 = **3.75** (empata con #2; desempata la fuente primaria)
- **Evidencia de demanda:**
  - Latam: una oferta remota Latam (SumerSports vía Fuel Talent) pide Databricks, Airflow o Dagster y lista Kafka solo como deseable (https://www.simplyhired.mx/job/iRs0m1oI4fW21pfDkP-QQI6WyWVsOReMGDxveKBVb8HZMv2Wnf8lmw, consultada 2026-10-26, sin fecha de publicación; agregador). Kafka como requisito en Latam: **sin evidencia** → Latam = 2.
  - Global: ofertas senior con Kafka + dbt (EY GDS, 2026-04-30, India: https://careers.ey.com/ey/job/Bengaluru-EY-GDS-Consulting-AI-And-DATA-DBT-Kafka-Senior-KA-560016/1389332233/, consultada 2026-10-26) y Coherent Solutions (Kafka, Airflow, dbt: https://job-boards.eu.greenhouse.io/coherentsolutions/jobs/4754583101, consultada 2026-10-26). Un análisis de terceros cifra Kafka en 41% de ofertas (https://blog.dataengineerthings.org/stop-chasing-every-new-data-tool-here-is-the-real-data-engineering-stack-for-2026-bb7dcb131070, consultado 2026-10-26; **fuente de terceros**) → global = 3.
- **Desafío real que replica:** agregar eventos de conductores y pasajeros por celda geográfica y ventana de un minuto en tiempo casi real. Fuente primaria (Uber Engineering, no leída en completo): https://www.uber.com/en-MY/blog/building-scalable-streaming-pipelines (consultada 2026-10-26).
- **Fase 1 (3 semanas):** simulador/feed → Redpanda → consumidor Python → agregados por ventana y celda en Postgres; pruebas de datos y de consumidor; GitHub Actions con ramas y PRs (lint + pruebas); documentación y diagrama de arquitectura desde la semana 1. Dagster pasa a Fase 2.

## Fichas resumidas #2–#5

**#2 Torre de Control Logística (provisional: sin fuente primaria)** (Logística, consumo de API; reto: modelado). Ingesta periódica de APIs abiertas de envíos/clima/tráfico, orquestada con Dagster, modelo dimensional con snapshots de dbt y pruebas. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 por contrato LATAM con Python, dbt y Dagster: https://www.remotefront.com/remote-jobs/scale-army-data-engineer-04ku0, consultada 2026-10-26, agregador sin fecha / global 3, terceros) | dificultad 3 | reutilización 5 → **3.75**. Desafío real: sin blog primario verificado; pendiente.

**#3 Sensores Industriales en Series de Tiempo (provisional: sin fuente primaria)** (IoT/industria, streaming; reto: volumen). Sensores simulados por Redpanda hacia Postgres con particionado, retención por niveles y agregados continuos. Puntajes: huecos 4 | portafolio 4 | demanda 2.5 (Latam 2 **sin evidencia** / global 3) | dificultad 4 | reutilización 3 → **3.60**. Desafío real: manejar datos tardíos y reprocesamiento incremental; candidato primario: serie Psyberg del Netflix Tech Blog (nov. 2023), cuyo enlace exacto no se pudo verificar (solo cobertura de terceros: https://www.infoq.com/news/2024/01/netflix-incremental-processing, consultada 2026-10-26). Sigue provisional.

**#4 Observatorio de Calidad Clínica** (Salud, batch; reto: calidad de datos). Datos de salud abiertos o sintéticos con reglas de calidad por niveles (críticos vs. secundarios), pruebas dbt y CI que bloquea PRs. Puntajes: huecos 4 | portafolio 3 | demanda 3.0 (Latam 3 / global 3; fuentes de terceros) | dificultad 3 | reutilización 5 → **3.50**. Desafío real: clasificar datasets por niveles con SLAs y checks según criticidad. Fuente primaria (Uber Engineering, no leída en completo): https://www.uber.com/blog/operational-excellence-data-quality/ (consultada 2026-10-26).

**#5 Libro Mayor y Conciliación** (Finanzas, batch/CDC; reto: modelado y evolución de esquema). Libro de doble entrada sintético y conciliación contra archivos de liquidación simulados, con modelo dimensional, pruebas y detección de duplicados y referencias faltantes. Puntajes: huecos 3 | portafolio 4 | demanda 2.5 (Latam 2 **sin evidencia concreta** / global 3) | dificultad 3 | reutilización 5 → 0.90 + 1.00 + 0.50 + 0.45 + 0.50 = **3.35** (re-puntuado: antes 3.45 con Latam 3 sin sustento). Desafío real: conciliar archivos de liquidación de procesadores de pago con el libro interno (duplicados y referencias erróneas como causa principal de descuadres). Fuente primaria (Uber Engineering, no leída en completo): https://www.uber.com/us/en/blog/ubers-advanced-settlement-accounting-system (consultada 2026-10-26).

## Banca (#6–#10)

6. Medidores Inteligentes y Tarifas — Energía (batch; SQL avanzado, volumen) — **3.20**
7. Capa de Métricas Única para Marketplace — Retail/e-commerce (batch; modelado) — **3.10** (nuevo; repone al proyecto activo; inspirado en la capa de métricas de Airbnb, sin enlace primario verificado)
8. CDR Telecom con Evolución de Esquema — Telecom (streaming/batch; evolución de esquema) — **3.05**
9. Monitor de Precios y Promociones — Retail/e-commerce (consumo de API; calidad de datos) — **2.75**
10. Demanda Energética con APIs Abiertas — Energía (consumo de API; modelado) — **2.70**

## Qué cambió esta semana y por qué

- "CDC Retail Orquestado" es el proyecto activo y debe quedar fuera del pool; la ejecución anterior lo había dejado en #1. Se excluyó y se repuso con "Capa de Métricas Única para Marketplace". Por eso todos los demás suben de posición.
- Telemetría de Flota pasa a #1 (empata con Torre en 3.75; gana por tener fuente primaria).
- Libro Mayor consigue fuente primaria (Uber, liquidación y conciliación) y entra al top 5; Sensores baja a provisional #3 pero se mantiene por puntaje.
- Evidencia Latam nueva: un contrato LATAM con Dagster + dbt (sostiene Latam 3 en Torre) y una oferta Latam con Kafka solo como deseable (Latam 2 en streaming). No se encontraron ofertas en GetOnBoard ni LinkedIn.
- Pendiente: verificar el contenido y fecha de los blogs primarios y hallar fuente primaria para Logística y Sensores.

## Proyectos previos

_(Sección fija: la edita el usuario. Aún vacía.)_

# Ranking vivo de proyectos

**Proyecto activo:** CDC Retail Orquestado

**Ejecución:** 2026-11-02 (Δ contra el ranking del 2026-10-07)

> Nota de método: los sitios de blogs de ingeniería (Uber, Netflix) y GetOnBoard no se pudieron abrir desde el entorno (dominios fuera de la red permitida); habría que habilitar uber.com, netflixtechblog.com y getonbrd.com en la configuración de red de la sesión. Los enlaces primarios provienen de ejecuciones anteriores y NO se releyeron ni se confirmó su fecha. La evidencia de demanda proviene de resultados de búsqueda (fecha de consulta 2026-11-02).

## Top 5

| # | Proyecto | Dominio | Carga | Total | Δ |
|---|----------|---------|-------|-------|---|
| 1 | Torre de Control Logística (provisional: sin fuente primaria) | Logística | Consumo de API | 3.75 | ▲2 |
| 2 | Telemetría de Flota en Vivo | Movilidad | Streaming | 3.70 | = (0) |
| 3 | Observatorio de Calidad Clínica | Salud | Batch | 3.50 | ▲2 |
| 4 | Sensores Industriales en Series de Tiempo (provisional: sin fuente primaria) | IoT/industria | Streaming | 3.45 | = (0) |
| 5 | Libro Mayor y Conciliación (provisional: sin fuente primaria) | Finanzas | Batch/CDC | 3.45 | ▲1 |

Variedad: top 3 con dominios distintos (logística, movilidad, salud); 4 tipos de carga en el top 5 (API, streaming, batch, CDC). Solo #2 y #3 tienen fuente primaria; los otros tres completan el top 5 como provisionales. "CDC Retail Orquestado" sale del pool por ser el proyecto activo.

## Ficha completa #1 — Torre de Control Logística (provisional: sin fuente primaria)

- **Dominio:** Logística
- **Tipo de carga:** Consumo de API (reto principal: modelado)
- **Resumen:** Una operadora de envíos necesita ver el estado de sus entregas junto con clima y tráfico, pero los datos llegan de APIs abiertas con cortes, límites de uso y cambios de formato. El proyecto ingiere esas APIs de forma periódica e idempotente, las modela en capas medallón con esquema dimensional (con historial vía snapshots) y las entrega probadas y orquestadas.
- **Stack:** Python, SQL, PostgreSQL, dbt, Docker, VPS, arquitectura medallón (dominados) + **Dagster (nuevo)**, **GitHub Actions (nuevo)**. Asset checks de Dagster y snapshots de dbt como funciones nuevas de herramientas ya conocidas.
- **Huecos que cierra:** orquestación, testing de datos, CI/CD, git con ramas y PRs, modelado dimensional.
- **Pros:**
  - Ataca orquestación con Dagster, un hueco prioritario, usando solo herramientas ligeras.
  - Máxima reutilización del stack (Postgres, dbt, medallón); riesgo bajo de no terminar en 2-4 semanas.
  - Complementa el proyecto activo (CDC + Redpanda) sin repetir su dominio ni su tipo de carga.
- **Contras:**
  - No cubre streaming.
  - Sin fuente primaria verificada del desafío real.
  - Dificultad moderada: el valor depende de cuidar bien el modelado y los tests.
- **Puntajes (1-5):** Cierre de huecos 4 | Valor para portafolio 4 | Demanda 3.0 (Latam 3 / global 3) | Dificultad/aprendizaje 3 | Reutilización del stack 5
- **Total:** 4×0.30 + 4×0.25 + 3.0×0.20 + 3×0.15 + 5×0.10 = 1.20 + 1.00 + 0.60 + 0.45 + 0.50 = **3.75**
- **Evidencia de demanda:**
  - Latam: oferta remota "Senior Data Engineer" para cualquier país de Latam que pide Dagster (o Airflow/Prefect) y Kafka/Kinesis, con origen indicado como GetOnBoard (https://remotejobs.lat/es/job-offers/45660-senior-data-engineer, consultada 2026-11-02; sin fecha de publicación visible). Oferta Pavago para Brasil, Costa Rica y Argentina con Airflow/Prefect/Dagster/Luigi (https://echojobs.io/job/pavago-data-engineer-es4d2, consultada 2026-11-02; sin fecha visible). Previas: Muttdata (dbt) y Ryzlabs (dbt + Airflow, 2026-07-07: https://jobera.com/job/ryzlabs-data-engineer-61df6ce2/). Ofertas sin fecha confirmada: puntaje conservador de 3.
  - Global: un agregador reporta cerca de 700 ofertas con Airflow y 130 con Dagster, unas 30 con ambos (https://datadriven.io/airflow-data-engineer-jobs, consultado 2026-11-02; **fuente de terceros**, fecha no confirmada), por lo que global = 3.
- **Desafío real que replica:** sin evidencia de una fuente primaria específica (blog de ingeniería de empresa); pendiente de búsqueda. Contexto general sobre backfills idempotentes solo en fuentes de terceros.
- **Fase 1:** no aplica (solo 2 herramientas nuevas). Alcance sugerido de 3 semanas: ingesta idempotente de 2-3 APIs, medallón con dbt (dimensiones y snapshots), asset checks y pruebas dbt, CI en GitHub Actions con PRs, documentación y diagrama desde la semana 1.

## Fichas resumidas #2–#5

**#2 Telemetría de Flota en Vivo** (Movilidad, streaming; reto: latencia). Feed de posiciones de vehículos (datos abiertos de transporte) por Redpanda, consumidores en Python y agregación por ventanas y celdas geográficas en Postgres. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 por ofertas con Kafka sin fecha confirmada: https://job-boards.greenhouse.io/techietalent/jobs/4572950005, consultada 2026-11-02 / global 3, fuentes de terceros) | dificultad 4 | reutilización 3 → **3.70**. Desafío real: agregar eventos por celda geográfica y ventana de un minuto en tiempo casi real. Fuente primaria (Uber Engineering, no releída): https://www.uber.com/en-MY/blog/building-scalable-streaming-pipelines (de la consulta 2026-10-07).

**#3 Observatorio de Calidad Clínica** (Salud, batch; reto: calidad de datos). Datos de salud abiertos o sintéticos con reglas de calidad por niveles, pruebas dbt y CI que bloquea PRs. Puntajes: huecos 4 | portafolio 3 | demanda 3.0 (Latam 3 / global 3) | dificultad 3 | reutilización 5 → **3.50**. Desafío real: clasificar datasets por niveles con SLAs y checks según criticidad. Fuente primaria (Uber Engineering, no releída): https://www.uber.com/blog/operational-excellence-data-quality/ (consultada 2026-10-07).

**#4 Sensores Industriales en Series de Tiempo (provisional: sin fuente primaria)** (IoT/industria, streaming; reto: volumen). Sensores simulados por Redpanda hacia Postgres con particionado, retención y agregados por hora. Puntajes: huecos 4 | portafolio 3 (se solapa con #2) | demanda 3.0 (Latam 3 por ofertas con Kafka / global 3) | dificultad 4 | reutilización 3 → **3.45**. Desafío real: sin evidencia de blog primario; las búsquedas de esta semana solo arrojan guías y posts de proveedores.

**#5 Libro Mayor y Conciliación (provisional: sin fuente primaria)** (Finanzas, batch/CDC; reto: modelado y evolución de esquema). Conciliación de movimientos contables con modelo dimensional e historial de cambios, pruebas de integridad y CI. Puntajes: huecos 3 | portafolio 4 | demanda 3.0 (Latam 3 / global 3) | dificultad 3 | reutilización 5 → **3.45**. Desafío real: sin evidencia de blog primario; pendiente.

## Banca (#6–#10)

6. Medidores Inteligentes y Tarifas — Energía (batch; SQL avanzado, volumen) — **3.20**
7. CDR Telecom con Evolución de Esquema — Telecom (streaming/batch; evolución de esquema) — **3.05**
8. Detección de Fraude en Pagos en Streaming — Finanzas (streaming; latencia) — **3.00** (nuevo; repone al proyecto activo)
9. Monitor de Precios y Promociones — Retail/e-commerce (consumo de API; calidad de datos) — **2.75**
10. Demanda Energética con APIs Abiertas — Energía (consumo de API; modelado) — **2.70**

## Qué cambió esta semana y por qué

- "CDC Retail Orquestado" es el proyecto activo y sale del ranking (antes #1); se repone con "Detección de Fraude en Pagos en Streaming" en la banca. Los demás suben de puesto por ello.
- Hay ofertas Latam concretas con Dagster y Kafka (Ruzora, Pavago, Techie Talent), aunque sin fecha confirmada; permiten Latam = 3 en los proyectos de streaming y orquestación (antes 2 por "sin evidencia"). Ninguna oferta menciona Redpanda.
- Telemetría sube de 3.75 a 3.70 neto: demanda sube a 3.0, pero la dificultad se puntúa 4 y no 5. Sensores baja a 3.45 (portafolio 3 por solaparse con Telemetría). Torre de Control queda #1 por score, aunque provisional.
- Sin cambios de fuentes primarias: siguen faltando para Logística, Sensores y Libro Mayor. Pendiente: habilitar acceso a blogs y GetOnBoard para verificarlas.

## Proyectos previos

_(Sección fija: la edita el usuario. Aún vacía.)_

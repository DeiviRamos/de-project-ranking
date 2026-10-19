# Ranking vivo de proyectos

**Proyecto activo:** CDC Retail Orquestado

**Ejecución:** 2026-10-19 (Δ contra el ranking del 2026-10-07)

> Nota de método: fechas de fuentes = fecha de consulta (2026-10-19). Por segunda semana los sitios de blogs de ingeniería (Uber, etc.) no se pudieron abrir desde el entorno (bloqueo de red); los enlaces primarios provienen de resultados de búsqueda, sin lectura completa ni fecha de publicación confirmada. La evidencia Latam sigue siendo escasa y se puntúa de forma conservadora.

## Top 5

| # | Proyecto | Dominio | Carga | Total | Δ |
|---|----------|---------|-------|-------|---|
| 1 | Telemetría de Flota en Vivo | Movilidad | Streaming | 3.75 | ▲1 |
| 2 | Torre de Control Logística (provisional: sin fuente primaria) | Logística | Consumo de API | 3.75 | ▲1 |
| 3 | Pagos Idempotentes en Streaming | Finanzas | Streaming | 3.60 | nuevo |
| 4 | Sensores Industriales en Series de Tiempo (provisional: sin fuente primaria) | IoT/industria | Streaming | 3.60 | = (0) |
| 5 | Observatorio de Calidad Clínica | Salud | Batch | 3.50 | = (0) |

Variedad: top 3 con dominios distintos (movilidad, logística, finanzas); 3 tipos de carga en el top 5 (streaming, API, batch). Solo 3 proyectos (#1, #3, #5) tienen fuente primaria; #2 y #4 completan el top 5 como provisionales.

## Ficha completa #1 — Telemetría de Flota en Vivo

- **Dominio:** Movilidad
- **Tipo de carga:** Streaming (reto principal: latencia)
- **Resumen:** Una operación de transporte necesita saber, casi en tiempo real, cuántos vehículos hay por zona geográfica y cómo cambia la oferta minuto a minuto. El proyecto ingiere un feed abierto de posiciones de vehículos, lo transporta por un bus de eventos y lo agrega por ventanas de tiempo y celdas geográficas, dejando tablas consultables en Postgres.
- **Stack:** Python, SQL, PostgreSQL, dbt, Docker, VPS (dominados) + **Redpanda (nuevo)**, **GitHub Actions (nuevo)**, **Dagster (nuevo; si el proyecto activo aún no lo cubrió)**. Tres herramientas nuevas como máximo: no exige Fase 1.
- **Huecos que cierra:** streaming, testing de datos (contratos de eventos, pruebas de latencia), CI/CD, git con ramas y PRs, SQL avanzado (ventanas, agregaciones espaciales).
- **Pros:**
  - Streaming con ventanas es el hueco con mayor peso que el proyecto activo solo toca parcialmente (CDC, no agregación).
  - Datos abiertos de transporte: gratis y reales.
  - Reutiliza Redpanda del proyecto activo, lo que acorta la curva.
- **Contras:**
  - Solapa con el proyecto activo en Redpanda: el aprendizaje nuevo es menor que en un proyecto de otro tipo.
  - Demanda Latam de streaming sin evidencia verificable.
  - Dificultad alta en manejo de tiempo de evento y datos tardíos.
- **Puntajes (1-5):** Cierre de huecos 4 | Valor para portafolio 4 | Demanda 2.5 (Latam 2 / global 3) | Dificultad/aprendizaje 5 | Reutilización del stack 3
- **Total:** 4×0.30 + 4×0.25 + 2.5×0.20 + 5×0.15 + 3×0.10 = 1.20 + 1.00 + 0.50 + 0.75 + 0.30 = **3.75**
- **Evidencia de demanda:**
  - Latam: **sin evidencia** verificable de Kafka/Redpanda/streaming como requisito (una búsqueda de esta semana solo indica que Kafka aparece como "deseable" salvo en ofertas senior, sin enlace concreto verificado; consultada 2026-10-19). Latam limitado a 2.
  - Global: ofertas remotas que combinan Dagster/Airflow con dbt (búsqueda del 2026-10-19; agregadores como https://www.itjobswatch.co.uk/jobs/work%20from%20home/dagster.do?p=6, consultado 2026-10-19; **fuente de terceros**). Streaming específico: reporte de terceros de Airflow 48% / Kafka 41% (https://blog.dataengineerthings.org/stop-chasing-every-new-data-tool-here-is-the-real-data-engineering-stack-for-2026-bb7dcb131070, consultado 2026-10-19; fuente de terceros). Global = 3.
- **Desafío real que replica:** agregar eventos de conductores y pasajeros por celda geográfica y ventana de un minuto en tiempo casi real, con suavizado espacial. Fuente primaria (Uber Engineering, sin leer en completo esta semana): https://www.uber.com/en-MY/blog/building-scalable-streaming-pipelines (consultado 2026-10-19).
- **Fase 1:** no aplica (3 herramientas nuevas).

## Fichas resumidas #2–#5

**#2 Torre de Control Logística (provisional: sin fuente primaria)** (Logística, consumo de API; reto: modelado). Ingesta periódica de APIs abiertas de envíos/clima/tráfico, orquestada con Dagster, modelo dimensional con snapshots de dbt y pruebas. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3: ofertas con dbt y Airflow, p. ej. DaCodes México, publicada 2026-06-16, https://apply.workable.com/dacodes-mx/jobs/view/22C94314F5.md, consultada 2026-10-19 / global 3, fuentes de terceros) | dificultad 3 | reutilización 5 → **3.75**. Desafío real: sin blog primario verificado (un resultado sobre orquestación con Airflow en DoorDash se encontró sin enlace verificable); pendiente.

**#3 Pagos Idempotentes en Streaming** (Finanzas, streaming; reto: calidad de datos). Flujo simulado de transacciones de pago por Redpanda con duplicados y reintentos; consumidor idempotente que escribe en Postgres sin duplicar ni omitir tras fallos, con pruebas de recuperación y CI. Puntajes: huecos 4 | portafolio 4 | demanda 2.5 (Latam 2 por **sin evidencia** / global 3, terceros) | dificultad 4 | reutilización 3 → **3.60**. Desafío real: alinear los offsets consumidos con los commits de escritura para que un fallo no cause datos omitidos o duplicados. Fuente primaria (Uber Engineering, sin leer en completo): https://www.uber.com/en-IN/blog/from-batch-to-streaming-accelerating-data-freshness-in-ubers-data-lake/ (consultado 2026-10-19).

**#4 Sensores Industriales en Series de Tiempo (provisional: sin fuente primaria)** (IoT/industria, streaming; reto: volumen). Sensores simulados por Redpanda hacia Postgres con particionado, retención y vistas agregadas. Puntajes: huecos 4 | portafolio 4 | demanda 2.5 (Latam 2 por **sin evidencia** / global 3) | dificultad 4 | reutilización 3 → **3.60**. Desafío real: búsqueda de esta semana solo devolvió guías de proveedores (fuentes de terceros); pendiente.

**#5 Observatorio de Calidad Clínica** (Salud, batch; reto: calidad de datos). Datos de salud abiertos o sintéticos con reglas de calidad por niveles (críticos vs. secundarios), pruebas dbt y CI que bloquea PRs. Puntajes: huecos 4 | portafolio 3 | demanda 3.0 (Latam 3 / global 3; fuente de terceros https://www.thirstysprout.com/post/data-engineering-skills-required, consultada 2026-10-19) | dificultad 3 | reutilización 5 → **3.50**. Desafío real: clasificar datasets por niveles con SLAs y checks estándar según criticidad. Fuente primaria (Uber Engineering, sin leer en completo): https://www.uber.com/blog/operational-excellence-data-quality/ (consultado 2026-10-19).

## Banca (#6–#10)

6. Libro Mayor y Conciliación — Finanzas (batch/CDC; modelado y evolución de esquema) — **3.45**
7. Medidores Inteligentes y Tarifas — Energía (batch; SQL avanzado, volumen) — **3.20**
8. CDR Telecom con Evolución de Esquema — Telecom (streaming/batch; evolución de esquema) — **3.05**
9. Monitor de Precios y Promociones — Retail/e-commerce (consumo de API; calidad de datos) — **2.75**
10. Demanda Energética con APIs Abiertas — Energía (consumo de API; modelado) — **2.70**

## Qué cambió esta semana y por qué

- "CDC Retail Orquestado" es ahora el proyecto activo y se excluyó del pool (antes #1, 4.45). Todos los demás subieron una posición o se mantuvieron.
- Se repuso el décimo lugar con "Pagos Idempotentes en Streaming" (nuevo, #3), que tiene fuente primaria (Uber, de batch a streaming en el data lake) y cierra streaming y testing de datos.
- Evidencia Latam nueva: DaCodes (México, 2026-06-16) pide orquestación con Airflow/dbt, lo que sostiene Latam = 3 para Logística y Calidad Clínica. Kafka/Redpanda en Latam sigue sin evidencia verificable (Latam = 2 en los proyectos de streaming).
- Búsqueda de fuente primaria para Logística y Sensores: sin resultados (solo recursos de proveedores y reclutamiento); siguen provisionales.
- Limitación: los blogs de ingeniería no se pudieron abrir; enlaces primarios sin verificar en contenido ni fecha. Pendiente: verificarlos y conseguir fuente primaria para Logística y Sensores.

## Proyectos previos

_(Sección fija: la edita el usuario. Aún vacía.)_

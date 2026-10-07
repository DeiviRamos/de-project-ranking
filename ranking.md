# Ranking vivo de proyectos

**Ejecución:** 2026-10-06 (primera ejecución; todos los Δ = "nuevo")

> Nota de método: las fechas de las fuentes son la fecha de consulta (2026-10-06); los buscadores no devolvieron fecha de publicación fiable. La evidencia de demanda Latam es escasa: se puntúa conservadoramente.

## Top 5

| # | Proyecto | Dominio | Carga | Total | Δ |
|---|----------|---------|-------|-------|---|
| 1 | CDC Retail Orquestado | Retail/e-commerce | CDC | 4.55 | nuevo |
| 2 | Torre de Control Logística | Logística | Consumo de API | 3.95 | nuevo |
| 3 | Telemetría de Flota en Vivo | Movilidad | Streaming | 3.85 | nuevo |
| 4 | Observatorio de Calidad Clínica | Salud | Batch | 3.60 | nuevo |
| 5 | Sensores Industriales en Series de Tiempo | IoT/industria | Streaming | 3.60 | nuevo |

## Ficha completa #1 — CDC Retail Orquestado

- **Dominio:** Retail/e-commerce
- **Tipo de carga:** CDC (reto principal: evolución de esquema y calidad de datos)
- **Resumen:** Una tienda en línea simulada opera sobre una base transaccional (pedidos, clientes, inventario). El negocio necesita analítica casi en tiempo real sin consultar la base operativa. El proyecto captura los cambios de esa base, los transporta por un bus de eventos y los modela en capas medallón con un esquema dimensional (incluyendo historial de cambios), todo orquestado y probado.
- **Stack:** Python, SQL, PostgreSQL, dbt, Docker, VPS, arquitectura medallón (dominados) + **Debezium (nuevo)**, **Redpanda (nuevo)**, **Dagster (nuevo)**, **GitHub Actions (nuevo)**, dbt tests + asset checks de Dagster (nuevo).
- **Huecos que cierra:** streaming, orquestación, testing de datos, CI/CD, git con ramas y PRs, modelado dimensional (SCD).
- **Pros:**
  - Cubre 6 de los 7 huecos prioritarios en un solo proyecto.
  - Extiende lo que ya dominas (Postgres, dbt, medallón) en lugar de empezar de cero.
  - Todo corre en Docker, costo cero, y hay un lab oficial de referencia.
- **Contras:**
  - Tres herramientas nuevas a la vez; riesgo de pasar de 4 semanas.
  - Debezium/conectores requieren depuración de configuración de replicación lógica.
  - Sin volumen real: la demostración de escala será sintética.
- **Puntajes (1-5):** Cierre de huecos 5 | Valor para portafolio 5 | Demanda 3.5 (Latam 3 / global 4) | Dificultad/aprendizaje 4 | Reutilización del stack 5
- **Total:** 5×0.30 + 5×0.25 + 3.5×0.20 + 4×0.15 + 5×0.10 = **4.55**
- **Evidencia de demanda:**
  - Global: un análisis de ofertas 2026 reporta Airflow en 48% de roles de data engineering y Kafka en 41%, y dbt en 33% (consultado 2026-10-06): https://blog.dataengineerthings.org/stop-chasing-every-new-data-tool-here-is-the-real-data-engineering-stack-for-2026-bb7dcb131070 (fuente de blog de terceros, no un conteo oficial; puntuado 4, no 5).
  - Global: otra guía indica que Airflow y Kafka suelen aparecer como "preferidos" más que como requeridos (consultado 2026-10-06): https://www.thirstysprout.com/post/data-engineering-skills-required
  - Latam: un análisis de 1,467 ofertas muestra CI/CD en 16.2% y Python/SQL en torno al 70% (consultado 2026-10-06): https://bertonisolutions.com/blog/hiring-data-engineers-latam-2026 . Streaming/Kafka en Latam: **sin evidencia** concreta de porcentaje; la oferta de GetOnBoard (https://www.getonbrd.com/empleos/data-science-analytics/data-engineer-decision-point-latam-ciudad-de-mexico-santiago-3614, consultada 2026-10-06) no verifiqué en detalle. Por eso Latam = 3.
- **Desafío real que replica:** mover cambios de bases operativas a destinos analíticos sin cargas batch pesadas. Netflix construyó DBLog para esto (resumen en VentureBeat, consultado 2026-10-06): https://venturebeat.com/business/change-data-capture-the-critical-link-for-airbnb-netflix-and-uber . Referencia técnica de implementación: https://docs.redpanda.com/labs/docker-compose/cdc-postgres-json.md

## Fichas resumidas #2–#5

**#2 Torre de Control Logística** (Logística, consumo de API; reto: modelado). Ingesta periódica de APIs abiertas de envíos/clima/tráfico, orquestada con Dagster, y modelo dimensional con snapshots de dbt y pruebas. Puntajes: huecos 4 | portafolio 4 | demanda 4 (Latam 4 / global 4, evidencia genérica de Airflow/dbt arriba) | dificultad 3 | reutilización 5 → **3.95**. Desafío real: sin evidencia de blog específico; pendiente de investigar.

**#3 Telemetría de Flota en Vivo** (Movilidad, streaming; reto: latencia). Feed de vehículos (p. ej. datos abiertos de transporte) por Redpanda, consumidores en Python y agregaciones ventana en Postgres. Puntajes: huecos 4 | portafolio 4 | demanda 3 (Latam 2 por **sin evidencia** / global 4) | dificultad 5 | reutilización 3 → **3.85**. Desafío real: procesar eventos de ubicación con latencia baja; blog específico pendiente (sin evidencia aún).

**#4 Observatorio de Calidad Clínica** (Salud, batch; reto: calidad de datos). Datos de salud abiertos/sintéticos con reglas de calidad por niveles (críticos vs. secundarios), dbt tests y asset checks, CI que bloquea PRs. Puntajes: huecos 4 | portafolio 3 | demanda 3.5 (Latam 3 / global 4; calidad de datos en 43% de ofertas según https://www.thirstysprout.com/post/data-engineering-skills-required , consultado 2026-10-06) | dificultad 3 | reutilización 5 → **3.60**. Desafío real: Uber clasifica datasets por tier y aplica checks automáticos: https://bigeye.com/blog/data-in-practice-systematizing-data-quality-at-uber-scale (consultado 2026-10-06).

**#5 Sensores Industriales en Series de Tiempo** (IoT/industria, streaming; reto: volumen). Sensores simulados por Redpanda hacia Postgres con particionado y retención, vistas agregadas. Puntajes: huecos 4 | portafolio 4 | demanda 2.5 (Latam 2 / global 3) | dificultad 4 | reutilización 3 → **3.60**. Desafío real: sin evidencia de blog específico.

## Banca (#6–#10)

6. Libro Mayor y Conciliación — Finanzas (batch/CDC; modelado y evolución de esquema) — **3.45**
7. Medidores Inteligentes y Tarifas — Energía (batch; SQL avanzado, volumen) — **3.20**
8. CDR Telecom con Evolución de Esquema — Telecom (streaming/batch; evolución de esquema) — **3.05**
9. Monitor de Precios y Promociones — Retail/e-commerce (consumo de API; calidad de datos) — **2.75**
10. Demanda Energética con APIs Abiertas — Energía (consumo de API; modelado) — **2.70**

## Qué cambió esta semana y por qué

Primera ejecución: se creó el pool de 10 desde cero. El #1 gana por cubrir la mayoría de huecos prioritarios y extender el stack actual, no por moda. Cumple las reglas de variedad: top 3 con dominios distintos (retail, logística, movilidad) y 4 tipos de carga en el top 5 (CDC, API, streaming, batch). Limitaciones: la evidencia Latam es débil (no se pudo verificar GetOnBoard/LinkedIn con detalle) y los blogs de big tech solo respaldan #1 y #4; los demás desafíos reales quedan pendientes de investigar la próxima semana.

## Proyectos previos

_(Sección fija: la edita el usuario. Aún vacía.)_

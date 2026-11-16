# Ranking vivo de proyectos

**Proyecto activo:** CDC Retail Orquestado

**Ejecución:** 2026-11-16 (Δ contra el ranking del 2026-10-07)

> Nota de método: las fechas indicadas son la fecha de consulta (2026-11-16) salvo que se diga otra cosa. Desde el entorno no se pudieron abrir uber.com ni getonbrd.com (bloqueo de red); la evidencia proviene de resultados de búsqueda, sin leer el texto completo de las fuentes. Varias ofertas de GetOnBoard no muestran fecha de publicación en el resultado y algunas figuran cerradas. "CDC Retail Orquestado" pasó a ser el proyecto activo y se excluyó del pool.

## Top 5

| # | Proyecto | Dominio | Carga | Total | Δ |
|---|----------|---------|-------|-------|---|
| 1 | Telemetría de Flota en Vivo | Movilidad | Streaming | 3.85 | ▲1 |
| 2 | Libro Mayor y Conciliación | Finanzas | Batch/CDC | 3.75 | ▲4 |
| 3 | Torre de Control Logística (provisional: sin fuente primaria) | Logística | Consumo de API | 3.75 | = (0) |
| 4 | Integridad de Pagos en Streaming | Finanzas | Streaming | 3.70 | nuevo |
| 5 | Observatorio de Calidad Clínica | Salud | Batch | 3.50 | = (0) |

Variedad: top 3 con dominios distintos (movilidad, finanzas, logística); 4 tipos de carga en el top 5 (streaming, batch, CDC, API). Cuatro proyectos (#1, #2, #4, #5) tienen fuente primaria; #3 completa el top 5 como provisional. Empate en 3.75: #2 queda delante de #3 por tener fuente primaria.

## Ficha completa #1 — Telemetría de Flota en Vivo

- **Dominio:** Movilidad
- **Tipo de carga:** Streaming (reto principal: latencia)
- **Resumen:** Un operador de transporte necesita saber, minuto a minuto, dónde hay concentración o falta de vehículos y cuánto se desvían de su horario. El proyecto ingiere posiciones de vehículos (feed abierto en formato GTFS-Realtime o un simulador), las transporta por un bus de eventos y produce agregados por ventana de tiempo y celda geográfica, con un modelo histórico para análisis.
- **Stack:** Python, SQL, PostgreSQL, dbt, Docker, VPS, medallón (dominados) + **Redpanda (nuevo; se practica en el proyecto activo)**, **Dagster (nuevo)** para backfills y agregados diarios, **GitHub Actions (nuevo)**. Celdas geográficas con una grilla simple en SQL; una librería de índices hexagonales queda para una fase posterior, para no sumar una cuarta herramienta nueva.
- **Huecos que cierra:** streaming (principal), SQL avanzado (funciones de ventana, agregación temporal), testing de datos (pruebas sobre eventos tardíos y duplicados), CI/CD, git con ramas y PRs; orquestación y modelado dimensional solo de forma parcial (por eso 4 y no 5).
- **Pros:**
  - Extiende directamente lo aprendido en el proyecto activo (Redpanda) hacia procesamiento por ventanas, que es el siguiente escalón de streaming.
  - Problema fácil de explicar en entrevista (latencia, eventos fuera de orden, idempotencia) y con datos abiertos reales.
  - Costo cero: todo corre en Docker local o en el VPS.
- **Contras:**
  - Sin un motor de streaming dedicado, las ventanas se implementan en Python/Postgres; es una simplificación que hay que justificar en un ADR.
  - Depende de la disponibilidad y calidad del feed abierto elegido; conviene tener un simulador de respaldo.
  - Menor reutilización de dbt que los proyectos batch.
- **Puntajes (1-5):** Cierre de huecos 4 | Valor para portafolio 4 | Demanda 3.0 (Latam 3 / global 3) | Dificultad/aprendizaje 5 | Reutilización del stack 3
- **Total:** 4×0.30 + 4×0.25 + 3.0×0.20 + 5×0.15 + 3×0.10 = 1.20 + 1.00 + 0.60 + 0.75 + 0.30 = **3.85**
- **Evidencia de demanda:**
  - Latam: oferta remota de Coderslab.io en GetOnBoard (residencia en Chile, Perú o Colombia) que pide Kafka, Kafka Connect y procesos de streaming (https://www.getonbrd.com/jobs/data-science-analytics/data-engineer-coderslab-io-remote, consultada 2026-11-16; fecha de publicación no visible). Oferta de ingeniería con Kafka Streams y Kafka Connect de Wizeline en Colombia, publicada 2026-02-25 (https://hw.glich.co/jobboard/jobs/senior-kafka-software-engineer-at-wizeline-pbgn5h, consultada 2026-11-16; es un rol de software, no de datos puro). Orquestación con Airflow en ofertas de Santiago: 3IT (https://www.getonbrd.com/jobs/data-engineer-sr-3it-santiago) y Dynamic Devs (https://www.getonbrd.com/jobs/data-engineer-dynamic-devs-santiago), ambas consultadas 2026-11-16, sin fecha visible. Evidencia concreta pero escasa → Latam = 3.
  - Global: oferta remota de Fountain que pide migrar a streaming con Kafka y Debezium y orquestar dbt con Dagster (https://dynamitejobs.com/company/fountain/remote-job/senior-data-engineer, consultada 2026-11-16, fecha no confirmada); oferta remota de PadSplit con Dagster, dbt y Kafka (https://www.workingnomads.com/jobs/data-engineer-fully-remote-padsplit, consultada 2026-11-16); un buscador de empleo listaba 13 ofertas remotas con Dagster en Reino Unido (https://www.itjobswatch.co.uk/find/Work-from-Home-Dagster-jobs, consultada 2026-11-16). La mayoría exige residencia en EE. UU. o Reino Unido y son casos puntuales, no estadística → global = 3.
- **Desafío real que replica:** agregar eventos de vehículos por celda geográfica y ventana corta de tiempo en tiempo casi real, tolerando eventos tardíos. Fuentes primarias (no leídas en completo): Uber Engineering sobre pipelines de streaming escalables (https://www.uber.com/en-MY/blog/building-scalable-streaming-pipelines, consultada 2026-11-16) y DoorDash Engineering sobre su plataforma de eventos en tiempo real que publica agregados por ventana de tiempo (https://doordash.engineering/2022/08/02/building-scalable-real-time-event-processing-with-kafka-and-flink/, publicada 2022-08-02 según referencias secundarias). La escala se traduce a Redpanda + consumidores Python + Postgres, sin Flink.
- **Fase 1:** no es obligatoria (3 herramientas nuevas). Alcance sugerido de 3 semanas: ingesta del feed a Redpanda → bronce en Postgres; agregados por ventana y celda con pruebas de duplicados y eventos tardíos; GitHub Actions con ramas y PRs; documentación y diagrama de arquitectura desde la semana 1. Dagster entra en la semana 3 para backfills.

## Fichas resumidas #2–#5

**#2 Libro Mayor y Conciliación** (Finanzas, batch/CDC; reto: modelado). Eventos de pagos simulados se convierten en un libro mayor de doble partida, modelado dimensionalmente con dbt y conciliado contra extractos bancarios sintéticos; las pruebas exigen que cada asiento cuadre y que las diferencias de conciliación queden explicadas. Reutiliza la captura de cambios del proyecto activo. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 por ofertas con dbt/Airflow citadas arriba / global 3) | dificultad 3 | reutilización 5 → **3.75**. Desafío real: reemplazar un ETL nocturno que reconstruía la contabilidad a partir de registros de auditoría por un pipeline basado en eventos de movimiento de dinero. Fuente primaria (Airbnb Engineering, 2017, no leída en completo): https://medium.com/airbnb-engineering/6d742b80f040 (consultada 2026-11-16).

**#3 Torre de Control Logística (provisional: sin fuente primaria)** (Logística, consumo de API; reto: modelado). Ingesta periódica de APIs abiertas de envíos, clima y tráfico, orquestada con Dagster, con historial de estados de envío vía snapshots de dbt y pruebas. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 / global 3) | dificultad 3 | reutilización 5 → **3.75**. Desafío real: sin evidencia de blog primario; esta semana se buscó en Flexport, Shopify, Instacart y DoorDash y solo aparecieron documentación de API y fuentes de terceros.

**#4 Integridad de Pagos en Streaming** (Finanzas, streaming; reto: calidad de datos). Varios servicios simulados (checkout, pasarela, contabilidad) emiten eventos a Redpanda; un consumidor detecta pagos faltantes, duplicados o con montos distintos entre sistemas y publica métricas de integridad con SLA de detección. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 por ofertas Kafka / global 3) | dificultad 4 | reutilización 3 → **3.70**. Desafío real: medir la consistencia de transacciones entre sistemas de pago distribuidos. Fuente primaria (Airbnb Engineering, no leída en completo, fecha no confirmada): https://medium.com/airbnb-engineering/measuring-transactional-integrity-in-airbnbs-distributed-payment-ecosystem-a670d6926d22 (consultada 2026-11-16).

**#5 Observatorio de Calidad Clínica** (Salud, batch; reto: calidad de datos). Datos de salud abiertos o sintéticos con reglas de calidad por niveles (críticos vs. secundarios), pruebas dbt que bloquean la publicación de datos defectuosos y CI que bloquea PRs. Puntajes: huecos 4 | portafolio 3 | demanda 3.0 (Latam 3 / global 3) | dificultad 3 | reutilización 5 → **3.50**. Desafío real: clasificar datasets por criticidad con checks estándar (Uber, https://www.uber.com/blog/operational-excellence-data-quality/) y ejecutar checks dentro del pipeline antes de exponer los datos (Airbnb, https://medium.com/airbnb-engineering/how-airbnb-built-wall-to-prevent-data-bugs-ad1b081d6e8f); ambas fuentes primarias consultadas 2026-11-16, no leídas en completo.

## Banca (#6–#10)

6. Sensores Industriales en Series de Tiempo — IoT/industria (streaming; volumen) — **3.70** (sin fuente primaria: solo contenido de proveedores)
7. CDR Telecom con Evolución de Esquema — Telecom (streaming/batch; evolución de esquema) — **3.45**
8. Medidores Inteligentes y Tarifas — Energía (batch; SQL avanzado, volumen) — **3.20**
9. Monitor de Precios y Promociones — Retail/e-commerce (consumo de API; calidad de datos) — **2.80**
10. Demanda Energética con APIs Abiertas — Energía (consumo de API; modelado) — **2.65**

## Qué cambió esta semana y por qué

- "CDC Retail Orquestado" (el #1 anterior) es ahora el proyecto activo y salió del pool, lo que deja libre el #1; se agregó "Integridad de Pagos en Streaming" como reposición.
- Apareció evidencia Latam concreta de Kafka/streaming (Coderslab.io en GetOnBoard, Wizeline en Colombia). Con eso, los proyectos de streaming pasan de Latam 2 a Latam 3: Telemetría de Flota sube a 3.85 y queda #1; CDR Telecom sube de 3.05 a 3.45.
- La banca se re-puntuó a fondo con desglose explícito. "Libro Mayor y Conciliación" subió de 3.45 a 3.75 (huecos 4, portafolio 4) y consiguió fuente primaria (Airbnb), así que entra al top 5 en el #2.
- "Sensores Industriales" cae al #6: sigue sin fuente primaria (las búsquedas solo dieron contenido de proveedores) y ya hay cuatro proyectos con fuente primaria que la desplazan. "Torre de Control Logística" se mantiene como el único provisional del top 5.
- "Observatorio de Calidad Clínica" suma una segunda fuente primaria (Airbnb Wall).
- Demanda global: hay ofertas remotas reales con Dagster + dbt + Kafka (Fountain, PadSplit), pero son casos puntuales y en su mayoría solo para residentes en EE. UU.; la demanda global sigue en 3.
- Contexto del sector: Prefect anunció el 2026-07-13 la compra de Dagster Labs; según la prensa del sector, Dagster mantiene su nombre, su licencia open source y su hoja de ruta (https://thenewstack.io/prefect-acquires-dagster-orchestrator/, fuente de terceros, consultada 2026-11-16). No cambia los puntajes, pero conviene documentar en el ADR del orquestador por qué se eligió Dagster frente a Airflow. El reporte de dbt Labs "State of Analytics Engineering 2026" (2026-04-14) indica que la confianza y la gobernanza de los datos van por detrás de la adopción de IA (https://www.getdbt.com/resources/state-of-analytics-engineering-2026, encuesta de proveedor); refuerza el valor de testing de datos, pero sin dato de demanda.
- Limitación: uber.com y getonbrd.com no se pudieron abrir desde el entorno; pendiente verificar el contenido y la fecha de las fuentes primarias y buscar una fuente primaria para Logística y Sensores.

## Proyectos previos

_(Sección fija: la edita el usuario. Aún vacía.)_

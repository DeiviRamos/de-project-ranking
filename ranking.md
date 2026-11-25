# Ranking vivo de proyectos

**Proyecto activo:** Libro Mayor y Conciliación

**Ejecución:** 2026-11-23 (Δ contra el ranking del 2026-10-07)

> Nota de método: las fechas de las fuentes son la fecha de consulta (2026-11-23) salvo que se indique la fecha de publicación. Esta semana la descarga directa de páginas siguió bloqueada desde el entorno (stripe.dev, getonbrd.com, careersatdoordash.com no resolvieron); toda la evidencia proviene de resultados de búsqueda y de sus extractos. Los blogs primarios citados NO se leyeron en completo y el estado (abierta/cerrada) de las ofertas no se pudo confirmar.

## Top 5

| # | Proyecto | Dominio | Carga | Total | Δ |
|---|----------|---------|-------|-------|---|
| 1 | Libro Mayor y Conciliación | Finanzas | Batch | 3.90 | ▲5 |
| 2 | Telemetría de Flota en Vivo | Movilidad | Streaming | 3.85 | = (0) |
| 3 | Sensores Industriales en Series de Tiempo | IoT/industria | Streaming | 3.80 | ▲1 |
| 4 | Torre de Control Logística | Logística | Consumo de API | 3.75 | ▼1 |
| 5 | Observatorio de Calidad Clínica | Salud | Batch | 3.50 | = (0) |

Variedad: top 3 con dominios distintos (finanzas, movilidad, IoT/industria); 3 tipos de carga en el top 5 (batch, streaming, consumo de API). Los 5 proyectos tienen ahora "desafío real que replica" con enlace a blog de ingeniería de la empresa (sin lectura completa; ver nota de método).

## Ficha completa #1 — Libro Mayor y Conciliación

- **Dominio:** Finanzas
- **Tipo de carga:** Batch (extractos y movimientos diarios; reto principal: modelado y calidad de datos)
- **Resumen:** Una fintech simulada registra pagos, reembolsos y comisiones en su sistema operativo, y recibe a diario extractos de un banco y de una pasarela de pago. Finanzas necesita un libro mayor de partida doble confiable, conciliado contra las fuentes externas, con reportes de saldos por cuenta y período y alertas cuando algo no cuadra.
- **Stack:** Python, SQL, PostgreSQL, dbt (snapshots, modelos incrementales), Docker, VPS, arquitectura medallón (dominados) + **Dagster (nuevo; se reutiliza lo aprendido en el proyecto activo)**, **GitHub Actions (nuevo)**, **pruebas unitarias de dbt / paquete dbt-expectations (nuevo)**. Tres herramientas nuevas: no exige Fase 1.
- **Huecos que cierra:** modelado dimensional (hechos de asientos, dimensiones de cuenta y contraparte con historial), SQL avanzado (conciliación con joins difusos, ventanas, saldos acumulados), testing de datos (invariantes: débitos = créditos, saldos no negativos, unicidad de movimientos), orquestación (particiones diarias y reprocesos), CI/CD y git con ramas y PRs.
- **Pros:**
  - Cubre 6 de los 7 huecos sin repetir el foco del proyecto activo (streaming/CDC); profundiza en modelado y SQL avanzado, los dos huecos que el activo toca menos.
  - Las invariantes contables dan tests de datos con significado de negocio, fáciles de explicar en entrevista.
  - Máxima reutilización del stack (Postgres + dbt) y costo cero.
- **Contras:**
  - Sin streaming: no suma al hueco de streaming (ya cubierto por el proyecto activo).
  - El dominio contable exige estudiar partida doble y reglas de conciliación antes de modelar.
  - Volumen sintético; la escala no es el argumento del proyecto.
- **Puntajes (1-5):** Cierre de huecos 4 | Valor para portafolio 4 | Demanda 3.0 (Latam 3 / global 3) | Dificultad/aprendizaje 4 | Reutilización del stack 5
- **Total:** 4×0.30 + 4×0.25 + 3.0×0.20 + 4×0.15 + 5×0.10 = 1.20 + 1.00 + 0.60 + 0.60 + 0.50 = **3.90**
- **Evidencia de demanda:**
  - Latam: ofertas en GetOnBoard que piden orquestación y dbt: Yom, Santiago híbrido, ETL/ELT en Python orquestado con Airflow, rango de 2.000–2.500 USD brutos/mes (https://getonbrd.com/jobs/data-science-analytics/data-engineer-yom-yom-santiago); Niuro, remoto para residentes en Chile, Airflow + dbt (https://www.getonbrd.com/empleos/data-science-analytics/data-engineer-niuro-remote-8b48); BC Tecnología "Data Engineer – Plataforma de Datos", Santiago híbrido, orquestadores tipo Dagster, Airflow o Prefect (https://www.getonbrd.com/jobs/data-science-analytics/data-engineer-plataforma-de-datos-bc-tecnologia-santiago). Todas consultadas 2026-11-23; fecha de publicación no visible. Ofertas específicas de conciliación/finanzas en Latam: **sin evidencia**. Latam = 3.
  - Global/remoto: Prefect, Staff Data Engineer remoto con dbt y Dagster, publicada 2026-09-09 (https://www.purpose.jobs/discover/companies/prefect/jobs/92570689-staff-data-engineer); Pavago, Data Engineer remoto con dbt como preferido, publicada 2026-06-10 (https://apply.workable.com/pavago/jobs/view/840B07360B.md). Ambas consultadas 2026-11-23. Son ofertas individuales, sin dato agregado: global = 3.
  - Contexto del sector: el reporte State of Analytics Engineering 2026 de dbt Labs (publicado 2026-04-14, 363 encuestados) indica que la confianza y la gobernanza no avanzan al ritmo de la producción de analítica, y que los problemas de calidad y responsabilidad sobre los datos siguen sin resolverse (https://www.getdbt.com/blog/new-dbt-labs-report-finds-ai-driven-acceleration-is-outpacing-trust-and-governance, consultado 2026-11-23).
- **Desafío real que replica:** garantizar que todo movimiento de dinero quede contabilizado con partida doble sobre un registro inmutable de eventos, y validar de forma continua que los flujos cuadren, señalando qué parte del pipeline falló cuando no lo hacen. Fuente primaria (Stripe, sin leer en completo): https://stripe.dev/blog/ledger-stripe-system-for-tracking-and-validating-money-movement (consultado 2026-11-23). Complemento sobre reportes financieros a escala (Airbnb Engineering, sin leer en completo): https://medium.com/airbnb-engineering/6d742b80f040. Escalado al entorno del usuario: Postgres + dbt + Dagster en Docker, sin servicios de pago.
- **Fase 1:** no aplica (3 herramientas nuevas). Alcance sugerido de 3 semanas: semana 1, repo con ramas/PRs, CI en GitHub Actions, diagrama y README; semana 2, bronce/plata/oro con asientos de partida doble y pruebas de invariantes; semana 3, conciliación contra extractos, particiones diarias orquestadas y reporte de descuadres.

## Fichas resumidas #2–#5

**#2 Telemetría de Flota en Vivo** (Movilidad, streaming; reto: latencia). Feed de posiciones de vehículos (datos abiertos de transporte) por Redpanda, consumidores en Python y agregación por ventanas de tiempo y celdas geográficas en Postgres. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 / global 3) | dificultad 5 | reutilización 3 → **3.85**. Latam sube a 3 por ofertas con Kafka: BC Tecnología "Ingeniero/a Senior de Plataforma de Datos (Kafka & Nifi)", remoto (https://www.getonbrd.com/jobs/data-science-analytics/ingeniero-a-senior-de-plataforma-de-datos-kafka-nifi-bc-tecnologia-remote) y OpenVPN, Data Engineer remoto con Chile entre los países y Kafka como plataforma de streaming deseada (https://careers.openvpn.net/o/data-engineer-ai-platforms-latam), ambas consultadas 2026-11-23, fecha de publicación no confirmada. Contra: se solapa con el streaming del proyecto activo. Desafío real: agregar eventos por celda geográfica y ventana de un minuto en tiempo casi real. Fuente primaria (Uber Engineering, sin leer en completo): https://www.uber.com/en-MY/blog/building-scalable-streaming-pipelines (consultado 2026-10-07).

**#3 Sensores Industriales en Series de Tiempo** (IoT/industria, streaming; reto: volumen). Sensores simulados por Redpanda hacia Postgres con particionado por tiempo, retención automática, rollups (minuto/hora/día) y archivo frío consultable. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 por las ofertas Kafka de #2 / global 3) | dificultad 4 | reutilización 4 → **3.80**. Desafío real: mantener series de tiempo de sensores en Postgres con particiones que se eliminan pasado un umbral y datos fríos descargados a almacenamiento abierto sin perder consultabilidad. Fuente primaria (blog de ingeniería de Snowflake, sin leer en completo; se replica solo con Postgres, sin servicio de pago): https://www.snowflake.com/en/engineering-blog/postgres-time-series-iceberg/ (consultado 2026-11-23).

**#4 Torre de Control Logística** (Logística, consumo de API; reto: modelado). Ingesta periódica de APIs abiertas de clima/tráfico y eventos de envíos simulados, orquestada con Dagster, modelo dimensional con snapshots de dbt e indicadores de retraso por etapa. Puntajes: huecos 4 | portafolio 4 | demanda 3.0 (Latam 3 por ofertas Airflow/dbt de #1 / global 3) | dificultad 3 | reutilización 5 → **3.75**. Desafío real: detectar ralentizaciones de entrega a partir de señales operativas agregadas por ventanas de tiempo y explicarlas por etapa (asignación, retiro, traslado). Fuentes primarias (DoorDash Engineering, sin leer en completo): https://careersatdoordash.com/?p=1393 (señales en tiempo real para ETA) y https://careersatdoordash.com/?p=15341 (alertas de ralentización, oct. 2025), consultadas 2026-11-23.

**#5 Observatorio de Calidad Clínica** (Salud, batch; reto: calidad de datos). Datos de salud abiertos o sintéticos con reglas de calidad por niveles (críticos vs. secundarios), pruebas dbt y CI que bloquea PRs. Puntajes: huecos 4 | portafolio 3 | demanda 3.0 (Latam 3 / global 3) | dificultad 3 | reutilización 5 → **3.50**. Desafío real: clasificar datasets por niveles con SLA por defecto y un conjunto estándar de checks (frescura, completitud, semántica, consistencia). Fuente primaria (Uber Engineering, 2021, sin leer en completo): https://www.uber.com/blog/operational-excellence-data-quality/ y https://www.uber.com/blog/ubers-journey-toward-better-data-culture-from-first-principles/ (consultadas 2026-11-23).

## Banca (#6–#10)

6. Medidores Inteligentes y Tarifas — Energía (batch; SQL avanzado, volumen) — **3.20**
7. CDR Telecom con Evolución de Esquema — Telecom (streaming/batch; evolución de esquema) — **3.15**
8. Disponibilidad de Inventario en Tiempo Real (nuevo) — Retail/e-commerce (streaming; latencia; extiende el proyecto activo consumiendo su flujo CDC; fuente primaria: https://company.instacart.com/tech-innovation/instacarts-item-availability-architecture-solving-for-scale-and-consistency) — **3.10**
9. Monitor de Precios y Promociones — Retail/e-commerce (consumo de API; calidad de datos) — **2.75**
10. Demanda Energética con APIs Abiertas — Energía (consumo de API; modelado) — **2.70**

## Qué cambió esta semana y por qué

- **CDC Retail Orquestado sale del pool** por ser el Proyecto activo (regla de exclusión). Se repone con "Disponibilidad de Inventario en Tiempo Real" (#8), que lo extiende; queda en la banca porque su cierre de huecos se solapa casi por completo con el proyecto activo.
- **Libro Mayor y Conciliación sube de #6 a #1:** ahora tiene fuente primaria (Stripe Ledger, con complemento de Airbnb), y se re-puntuó con el criterio de complementar el proyecto activo: cubre modelado dimensional y SQL avanzado, que el activo trabaja menos, con solo 3 herramientas nuevas.
- **Evidencia Latam de Kafka encontrada** (BC Tecnología en GetOnBoard, OpenVPN remoto con Chile): Latam sube de 2 a 3 en los proyectos de streaming (#2, #3, #7). Las fechas de publicación siguen sin confirmar.
- **Sensores Industriales y Torre de Control Logística dejan de ser provisionales:** se encontró fuente primaria (Snowflake Engineering para series de tiempo en Postgres; DoorDash Engineering para señales de entrega). Sensores sube a #3 por mayor reutilización de Postgres (particionado y retención).
- **Contexto de herramientas:** Prefect anunció el 2026-07-13 la adquisición de Dagster Labs; Dagster mantiene nombre, licencia open source y hoja de ruta según el anuncio (https://dagster.io/blog/prefect-is-acquiring-dagster, consultado 2026-11-23). No cambia la recomendación de Dagster, pero conviene seguirlo. En Latam aparece una oferta que acepta "Dagster, Airflow o Prefect" indistintamente.
- **Pendiente:** leer en completo los blogs primarios y confirmar fechas y estado de las ofertas cuando la red lo permita; buscar fuente primaria para CDR Telecom y Medidores Inteligentes.

## Proyectos previos

_(Sección fija: la edita el usuario. Aún vacía.)_

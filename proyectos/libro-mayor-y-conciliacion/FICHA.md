# Ficha: Libro Mayor y Conciliación

> Copia de la ficha completa #1 de `ranking.md` (ejecución 2026-11-23, rama `main`). Al final se agrega el reparto del alcance entre la Etapa 1 y la Etapa 2.

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

## Alcance de este kit y reparto por etapas

La ficha no define una Fase 1, así que el kit cubre **el alcance completo** de la ficha (libro mayor, conciliación contra banco y pasarela, saldos por cuenta y período, alertas de descuadre). Ese alcance se construye en dos etapas, en orden. La Etapa 1 tiene que quedar terminada antes de empezar la Etapa 2.

### Etapa 1: v1 a mano (Python + PostgreSQL + cron)

Herramientas: Python (scripts propios, pandas opcional), PostgreSQL, cron en el VPS, pytest, GitHub Actions desde el primer commit, git con ramas y PRs. **Sin dbt ni Dagster.**

Qué va en esta etapa:
- Repo, ramas, PRs, CI con un test trivial desde el primer commit, spec técnico, diagrama de la v1 y README de portafolio (equivale a la "semana 1" de la ficha).
- Ingesta en Python de las cuatro fuentes diarias, con lectura robusta de formatos distintos, registro de qué archivo se cargó y cuándo, manejo de errores, reintentos y logging.
- Limpieza y normalización en Python/SQL, carga idempotente en Postgres (volver a correr un día no duplica nada).
- Libro mayor de partida doble: reglas de contabilización escritas por ti, asientos inmutables, correcciones por asientos nuevos.
- Conciliación contra la pasarela y el banco, con partidas abiertas y su antigüedad.
- Saldos por cuenta y período, y un reporte de descuadres.
- Tests en pytest de las funciones de ingesta y de las invariantes contables.
- Una corrida diaria programada con cron.

### Etapa 2: v2 migración (dbt + Dagster)

Herramientas nuevas: dbt (snapshots, modelos incrementales, pruebas unitarias, dbt-expectations), Dagster (particiones diarias, dependencias, reintentos, reprocesos).

Qué va en esta etapa:
- La transformación y el modelado de la v1 se pasan a dbt en capas bronce/plata/oro: snapshots para la historia de comercios, incrementales para movimientos y asientos, tests genéricos, unitarios y de invariantes.
- La ingesta, la corrida diaria y los reprocesos se orquestan con Dagster por particiones diarias, en lugar de cron.
- Tests de regresión que prueban que la v2 da los mismos asientos, saldos y partidas conciliadas que la v1 con la misma semilla.
- ADR que explica qué resolvió cada herramienta frente a la v1.

## Fases siguientes (fuera del alcance de este kit)

La ficha no define fases posteriores. Ideas para después, si el proyecto se extiende: cierre contable mensual con bloqueo de períodos, multimoneda completa con revaluación, y conciliación casi en tiempo real si alguna fuente llegara a emitir eventos.

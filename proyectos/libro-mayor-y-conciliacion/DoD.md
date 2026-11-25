# Definition of Done: Libro Mayor y Conciliación

Marca cada punto con evidencia (link a PR, archivo, comando o captura). Un punto sin evidencia no está hecho.

## Común (aplica desde el primer commit, en ambas etapas)

- [ ] Todo cambio entra por rama y PR, con historial de commits legible.
- [ ] CI corriendo desde el primer commit, aunque tenga un solo test trivial.
- [ ] Spec técnico escrito ANTES de codear (con supuestos y preguntas abiertas), a partir de `plantillas/spec-tecnico.md`.
- [ ] Tests de datos que crecen junto con el pipeline.
- [ ] ADRs por cada decisión relevante (`plantillas/adr-plantilla.md`).
- [ ] Diagrama de arquitectura actualizado.
- [ ] README de portafolio listo desde el inicio (`plantillas/README-portafolio.md`).
- [ ] El ambiente se levanta con un solo comando documentado.
- [ ] Idempotencia y manejo de errores y reintentos demostrados.

## Etapa 1: v1 a mano (Python + PostgreSQL + cron)

No se empieza la Etapa 2 hasta que todos estos puntos tengan evidencia.

- [ ] Sin dbt ni orquestador: la ingesta, la limpieza, la carga y los cálculos están en Python y SQL propios.
- [ ] La ingesta lee las cuatro fuentes diarias (sistema operativo, pasarela, banco, comercios) y los maestros, y deja registro de qué archivo se cargó, cuándo y con qué resultado.
- [ ] Manejo de errores explícito: un archivo faltante, mal formado o con columnas inesperadas no deja la base a medias, y queda registrado con un mensaje que se entiende.
- [ ] Reintentos acotados donde tenga sentido, documentados en un ADR.
- [ ] Logging con niveles y formato consistentes, en archivo o en salida estándar recogida por cron.
- [ ] Carga idempotente demostrada: correr dos veces el mismo día (o reprocesar un rango) da el mismo resultado, con una prueba que lo muestre.
- [ ] Libro mayor con partida doble: cada asiento cuadra, y las correcciones se hacen sin perder la trazabilidad de lo registrado antes.
- [ ] Conciliación contra la pasarela y el banco, con las partidas abiertas y su antigüedad a la vista.
- [ ] Saldos por cuenta y período, y un reporte diario de descuadres.
- [ ] Tests en pytest para las funciones de ingesta y transformación, y para las invariantes contables, corriendo en CI.
- [ ] La corrida diaria está programada en cron (línea de crontab versionada) y su salida queda registrada.
- [ ] El README explica cómo correr la v1 completa desde cero con la semilla por defecto.
- [ ] Respuestas del spec: cada pregunta abierta para el cliente tiene un supuesto declarado o una respuesta.

## Etapa 2: v2 migración (dbt + Dagster)

- [ ] Modelos dbt en capas, con fuentes declaradas, documentación y tests (genéricos, unitarios y de invariantes, incluido dbt-expectations donde aporte).
- [ ] Historia de los atributos que cambian (por ejemplo, el plan de cada comercio) modelada con snapshots, y modelos incrementales donde el volumen lo justifique.
- [ ] Orquestación con Dagster: particiones diarias, dependencias explícitas entre ingesta y transformación, reintentos configurados y un reproceso de un rango demostrado.
- [ ] La corrida diaria ya no depende de cron.
- [ ] Tests de regresión v1 vs v2: con la misma semilla y los mismos archivos, la v2 da los mismos asientos, saldos y partidas abiertas que la v1. Las diferencias aceptadas quedan explicadas.
- [ ] CI corre `dbt build` (o equivalente) y los tests de regresión en cada PR.
- [ ] ADR de migración: qué resolvió cada herramienta frente a la v1, qué se perdió y qué costó.
- [ ] README de portafolio con el diagrama de la v1 y de la v2, y la sección "qué cambió al migrar".

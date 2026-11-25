# Spec técnico: <título>

- Autor:
- Fecha:
- Estado: borrador | revisado | aprobado
- Etapa: 1 (v1 a mano) | 2 (v2 migración)

## Objetivo
<!-- Qué problema de negocio resuelve, para quién, y qué queda fuera de alcance. -->

## Datos disponibles
<!-- Fuentes, archivos, campos clave, volúmenes, frecuencia de entrega. Qué sabes y qué no sabes de cada una. -->

| Fuente | Entrega | Frecuencia | Clave | Lo que no sé todavía |
|---|---|---|---|---|
|   |   |   |   |   |

## Criterios de aceptación
<!-- Condiciones medibles y verificables, en lenguaje del cliente. -->
- [ ]

## Definition of done
<!-- Enlaza o adapta DoD.md. -->
- [ ]

## Supuestos y preguntas abiertas para el cliente
<!-- Obligatoria. Cada supuesto: qué asumes, riesgo si es falso, a quién se pregunta. -->

| # | Supuesto / pregunta | Riesgo si es falso | A quién | Estado |
|---|---------------------|--------------------|---------|--------|
|   |                     |                    |         |        |

---

## Etapa 1: v1 a mano (Python + PostgreSQL + cron)

### Diseño
<!-- Componentes, flujo de un día, esquema en Postgres, cómo se programa. -->

### Manejo de errores, reintentos y logging
<!-- Qué fallas esperas, qué hace el proceso ante cada una, qué queda registrado. -->

### Idempotencia y reprocesos
<!-- Cómo garantizas que correr dos veces no duplica; cómo reprocesas un rango. -->

### Estrategia de tests
<!-- Qué cubre pytest, qué invariantes de datos se prueban, qué corre en CI. -->

### Criterios de aceptación de la etapa
- [ ]

---

## Etapa 2: v2 migración (dbt + orquestador)

### Diseño
<!-- Capas, modelos, snapshots, incrementales, assets y particiones. -->

### Qué se migra y qué se mantiene
<!-- Pieza por pieza de la v1: dónde queda en la v2. -->

| Pieza de la v1 | En la v2 | Motivo |
|---|---|---|
|   |   |   |

### Tests de regresión v1 vs v2
<!-- Qué se compara, con qué datos y semilla, qué tolerancia, cómo corre en CI. -->

### Criterios de aceptación de la etapa
- [ ]

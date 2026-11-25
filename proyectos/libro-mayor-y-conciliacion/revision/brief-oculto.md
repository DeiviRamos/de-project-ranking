# Brief oculto (uso interno de evaluación)

## Contradicciones plantadas

### 1. "Conciliación en tiempo real, al minuto" vs. fuentes diarias y un cierre a las 8:30

- **Lo que pide:** el gerente general quiere un panel "en vivo", al minuto.
- **Lo que necesita:** el banco y la pasarela entregan una vez por día hábil (y el banco a veces tarde). Con esas fuentes no hay conciliación al minuto posible. Lo que la operación necesita es el **cierre del día anterior confiable antes de las 8:30**, porque a las 9:00 tesorería decide las dispersiones. El panel en vivo solo podría mostrar los movimientos internos, sin conciliar.
- **Qué hace un buen ingeniero:** lo dice explícitamente en el spec, propone un SLA de frescura por fuente (por ejemplo, "cierre de D disponible a las 8:30 de D+1 hábil; si falta el extracto, reporte parcial marcado como tal"), y deja el "tiempo real" fuera de alcance o como fase posterior, con su costo. No construye streaming.

### 2. "Que el sistema corrija el registro para que cuadre con el banco y la cuenta de diferencias quede en cero" vs. auditoría y trazabilidad

- **Lo que pide:** sobrescribir lo registrado para que coincida con el banco y no tener partidas pendientes.
- **Lo que necesita:** la observación de la auditora fue justamente por un saldo que cambió entre revisiones. Necesita un libro **inmutable**: las correcciones se hacen con asientos nuevos (reversos o ajustes) con su motivo, y los saldos de un período ya reportado se pueden reproducir. Además, muchas diferencias son **legítimas y temporales** (capturas en tránsito, liquidación a T+2, extracto atrasado): forzarlas a cero esconde los errores reales (doble dispersión, captura no liquidada, retención). Y el banco no siempre "manda": la retención no informada y la transacción fantasma de la pasarela son errores de la contraparte.
- **Qué hace un buen ingeniero:** separa diferencias de **tiempo** (partidas en tránsito con antigüedad) de diferencias **reales** (descuadres), propone un umbral de tolerancia y un flujo de aprobación de ajustes, y lo deja en un ADR.

### Ambigüedades adicionales (no son contradicciones, pero se deben preguntar)

- Umbral de tolerancia: "no me avisen de un peso" vs. "que no se escape nada".
- ¿Se devuelve la comisión al comercio cuando hay reembolso? (Comercial.)
- Tipo de cambio para los USD: ¿el de la pasarela o el oficial? ¿Cómo se registra la diferencia?
- Definición de "día": Santiago vs. UTC del sistema.
- Formato de salida para el directorio: los saldos mensuales tienen que poder bajarse a una planilla.
- Dos personas de TI y "nada que entienda una sola persona": documentación, ejecución con un comando, logs legibles.

## Preguntas que un buen ingeniero haría al cliente

1. ¿Qué decisión se toma con el panel "en vivo" que no se pueda tomar con el cierre de las 8:30? ¿Quién lo mira y cuándo?
2. ¿Qué pasa hoy si a las 8:30 no llegó la cartola? ¿Se dispersa igual? ¿Con qué información?
3. ¿Cuál es la regla de la auditora para corregir un período ya informado? ¿Hay un cierre de período que bloquee asientos?
4. ¿Qué monto o porcentaje de diferencia se considera tolerable y quién aprueba un ajuste?
5. ¿Cuántos días hábiles debe esperar una captura antes de considerarla perdida?
6. ¿La comisión se devuelve en reembolsos totales? ¿Y en parciales? ¿Está en el contrato con los comercios?
7. ¿Con qué tipo de cambio registra Contabilidad los pagos en USD y dónde se lleva la diferencia con la pasarela?
8. ¿La comisión que cobramos incluye IVA? ¿La de la pasarela?
9. ¿Quién recibe las alertas y por qué canal? ¿Qué debe hacer con cada una?
10. ¿Qué pasa con la plata de un comercio suspendido? ¿Se le sigue dispersando?
11. ¿Cuántos meses hacia atrás necesitan cargar y poder reprocesar?

## Criterios para evaluar el cumplimiento del brief

| Criterio | Cumple | No cumple |
|---|---|---|
| Detecta la contradicción 1 | El spec la nombra, propone SLA de frescura por fuente y deja el "en vivo" fuera o acotado | Promete tiempo real o lo ignora |
| Detecta la contradicción 2 | Libro inmutable con correcciones por asientos nuevos; distingue tránsito de descuadre; ADR | Sobrescribe asientos o fuerza diferencias a cero |
| Preguntas abiertas | El spec tiene al menos 5 de las preguntas de arriba (o equivalentes) con supuesto y riesgo | Sección vacía o genérica |
| Partida doble | Invariante débitos = créditos por asiento probada en tests | Solo hay movimientos sin contrapartida |
| Saldos por cuenta y período | Se puede pedir el saldo de cualquier cuenta a cualquier fecha y se reproduce igual en una corrida posterior | Saldos que cambian al reprocesar sin asiento que lo explique |
| Conciliación | Partidas abiertas con antigüedad, contra banco y pasarela; detecta la retención, la doble liquidación y la doble dispersión | Solo cruza por referencia exacta |
| Alertas y umbral | Umbral documentado; los redondeos no generan ruido pero quedan contabilizados | Alerta por cada peso o no alerta nada |
| SLA y fuente atrasada | El proceso sin extracto termina, entrega un reporte parcial marcado y completa al llegar el archivo | Se cae o espera indefinidamente |
| Salida para el directorio | Hay una forma documentada de exportar los saldos mensuales | No se consideró |
| Mantenibilidad | README reproducible, un comando, logs legibles, ADRs | Solo lo entiende el autor |
| Sin herramientas de pago | Todo corre en Docker/VPS | Usa servicios de pago |

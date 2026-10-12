# Brief oculto (uso interno de evaluación)

## Contradicciones plantadas
1. **"Tiempo real / al segundo" vs "no se puede tocar la tienda"** y "si algo llega con retraso, avísenme, pero no me cambien el número de ayer".
   - Necesidad real: frescura de minutos con cero carga sobre la fuente y números históricos estables; eventos tardíos no deben reescribir silenciosamente periodos cerrados.
2. **"Cada pedido y cliente exactamente una vez, sin repetidos" vs "no se pierda nada, ni lo cancelado ni lo borrado".**
   - Necesidad real: una vista vigente deduplicada Y un historial completo (borrados lógicos, versiones de cambios). La unicidad aplica a la vista vigente, no al historial.
3. (Ambigüedad) "Historial… lo suficiente" sin plazo de retención; "números que cuadren con la tienda" sin definir qué es una discrepancia aceptable.

## Preguntas que haría un buen ingeniero
- ¿Qué latencia es aceptable (segundos, minutos) y para qué decisión concreta?
- ¿Cuánto historial por cliente/pedido y por cuánto tiempo (retención, privacidad)?
- ¿"Cancelado" lo define la tienda o Atención? ¿Cuál es la definición oficial y quién arbitra?
- ¿Qué pasa con un dato que llega tarde sobre un día ya reportado: se corrige o se anota?
- ¿Cuándo es "duplicado" un cliente (mismo correo, otro formato)? ¿Quién decide la fusión?
- ¿Qué carga máxima tolera la base de la tienda y qué ventanas (Buen Fin) se evitan?
- ¿Cómo se avisa de un cambio de esquema y quién lo aprueba?
- ¿Qué significa "números confiables": qué conciliación y con qué tolerancia?

## Criterios para evaluar cumplimiento del brief
- Cero consultas analíticas a la fuente; captura sin bloquearla.
- Cambios de esquema no rompen el flujo y quedan documentados.
- Vista vigente sin duplicados y a la vez historial de cambios (con deletes) conservado.
- Tratamiento explícito y documentado de datos tardíos.
- Evidencia de conciliación contra la fuente (conteos, totales) con tolerancia declarada.
- Spec con supuestos y preguntas al cliente antes de codear; ADRs de las decisiones.
- Primera versión útil en el plazo de 3 semanas (alcance Fase 1 acotado).

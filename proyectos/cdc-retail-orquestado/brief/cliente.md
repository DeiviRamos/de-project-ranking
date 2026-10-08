# Correo de Patricia Domínguez, Gerente de Operaciones Comerciales — "Casa Brisa" (tienda en línea de hogar y electrónica)

**Asunto:** Necesito números del día sin que se caiga la tienda

Hola,

Te escribo porque ya no aguanto más los lunes. Cada lunes mi equipo (somos cuatro personas en Operaciones Comerciales) me pasa un Excel con las ventas y el estado de los pedidos, y para cuando lo veo ya es viejo y casi siempre alguien me dice "esto no cuadra con lo que ve Atención a Clientes". La semana pasada discutí veinte minutos con Rodrigo, el jefe de Atención, sobre cuántos pedidos estaban cancelados. Teníamos dos números distintos y los dos venían "del sistema".

Lo que quiero es ver, **en tiempo real**, cómo va la venta: pedidos del día, cuánto llevamos vendido, qué productos se están agotando y cuántos pedidos se atoran sin enviar. Me imagino un tablero que se actualice solo. Rodrigo también quiere el historial de a quién le vendimos qué, y que si un cliente cambia de ciudad o de correo no se pierda lo que había antes, "por si hay reclamos". No sé exactamente cuánto tiempo hacia atrás; digamos que lo suficiente.

Algo importante: Tomás, nuestro desarrollador de la tienda, me dice que la base de datos de producción ya anda justa y que no quiere que nadie le pegue consultas pesadas, sobre todo en Buen Fin. Así que **no se puede tocar la tienda ni agregarle carga**. Eso sí, Tomás sigue cambiando cosas de la tienda cuando le piden funciones nuevas (la semana pasada agregó un campo para clasificar clientes) y no quiero tener que avisarle cada vez ni que algo se rompa en silencio.

Sobre los datos: queremos que **cada pedido y cada cliente aparezcan exactamente una vez**, sin repetidos, y que los números siempre cuadren con lo que dice la tienda. Al mismo tiempo, no quiero que se pierda nada, ni lo que se canceló ni lo que se borró, porque Finanzas luego pregunta. Y los reportes tienen que estar "al segundo". Si algo llega con retraso, avísenme, pero no me cambien el número de ayer.

Presupuesto: básicamente cero. No tenemos dinero para licencias ni servicios en la nube este año; se tiene que poder correr con lo que ya tenemos, que es un servidor propio con Linux y la base de datos que usa la tienda. Lo que sí tenemos es gente que sabe leer SQL en Operaciones.

Lo necesito para antes de la temporada alta, o sea que cuento con ver una primera versión útil en unas tres semanas. No me interesa el diseño bonito del tablero todavía, me interesa que los números sean confiables y que me expliquen cómo sé que lo son.

Gracias,

**Patricia Domínguez**
Gerente de Operaciones Comerciales, Casa Brisa

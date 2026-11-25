# Diccionario de datos: Libro Mayor y Conciliación

Empresa simulada: **Pagoflux SpA**, una fintech que cobra pagos a nombre de comercios (con tarjeta, vía una pasarela, o por transferencia directa a su cuenta corriente), descuenta su comisión y le transfiere el saldo a cada comercio. Todos los datos son sintéticos. Los RUT tienen dígito verificador válido, pero son inventados.

Convenciones generales:
- Moneda base de la empresa: peso chileno (CLP, sin decimales). Algunos pagos con tarjeta llegan en dólares (USD, dos decimales).
- Zona horaria del negocio: `America/Santiago`. Cada fuente informa las fechas a su manera (ver cada tabla).
- Separador decimal `.` en todos los archivos, salvo en el extracto bancario.
- Los archivos son entregas: una vez entregado, el emisor no corrige un archivo. Si algo cambia, llega en una entrega posterior.

---

## 1. `sistema_operativo/movimientos_AAAA-MM-DD.csv`

Exportación diaria del sistema transaccional propio. Cada archivo trae los movimientos **creados o modificados** ese día (fecha UTC de `actualizado_en`). Un mismo movimiento puede aparecer en más de un archivo si cambió de estado. CSV, UTF-8, separador `,`.

| Campo | Tipo | Significado de negocio |
|---|---|---|
| `id_movimiento` | texto | Identificador del movimiento en el sistema propio |
| `tipo` | texto | `PAGO` (cobro de un comprador a un comercio), `COMISION` (lo que Pagoflux le cobra al comercio por un pago), `REEMBOLSO` (devolución al comprador de un pago anterior), `DISPERSION` (transferencia de Pagoflux al comercio con lo recaudado) |
| `id_comercio` | texto | Comercio al que pertenece el movimiento (ver maestro de comercios) |
| `id_movimiento_origen` | texto | Para `COMISION` y `REEMBOLSO`: el `PAGO` al que se refiere. Vacío en los demás tipos |
| `medio` | texto | `TARJETA` o `TRANSFERENCIA`. Vacío en `COMISION` |
| `monto` | decimal | Monto en la moneda del movimiento, siempre positivo. El sentido lo da el `tipo`. En `COMISION`, monto total cobrado al comercio, **con IVA incluido** |
| `moneda` | texto | `CLP` o `USD` |
| `estado` | texto | `APROBADO`, `RECHAZADO` o `PENDIENTE`. Solo los pagos pasan por `PENDIENTE`; se resuelven después |
| `referencia_externa` | texto | Identificador del movimiento fuera del sistema: en pagos y reembolsos con tarjeta, la referencia de la pasarela (`PSR-…`); en transferencias, el número de documento bancario (`TRF-…`, `DEV-…`, `DSP-…`) |
| `creado_en` | timestamp UTC (ISO 8601, `Z`) | Momento en que se creó el movimiento |
| `actualizado_en` | timestamp UTC (ISO 8601, `Z`) | Momento del último cambio de esa versión del movimiento |

## 2. `pasarela/liquidacion_AAAA-MM-DD.csv`

Reporte de la pasarela de pago con tarjeta. Cada archivo es una liquidación: las operaciones que la pasarela le paga (o le descuenta) a Pagoflux ese día hábil, con su comisión. El total neto de la liquidación se deposita en la cuenta corriente el mismo día. CSV, UTF-8, separador `,`.

| Campo | Tipo | Significado de negocio |
|---|---|---|
| `id_liquidacion` | texto | Identificador de la liquidación (`LIQ-AAAAMMDD`). Aparece como documento en el extracto bancario |
| `fecha_liquidacion` | fecha | Día hábil en que se paga la liquidación |
| `ref_transaccion` | texto | Referencia de la operación en la pasarela (`PSR-…`) |
| `fecha_transaccion` | timestamp **hora local de Santiago, sin zona** | Momento de la operación original según la pasarela |
| `tipo_operacion` | texto | `CAPTURA` (cobro), `DEVOLUCION` (reembolso), `CONTRACARGO` (el titular de la tarjeta desconoció la compra) |
| `moneda_original` | texto | Moneda en que se hizo la operación |
| `monto_original` | decimal | Monto en la moneda original. Negativo en devoluciones y contracargos |
| `tipo_cambio` | decimal | CLP por USD que aplicó la pasarela. Vacío si la operación fue en CLP |
| `monto_bruto_clp` | entero | Monto de la operación en CLP |
| `comision_pasarela` | entero | Comisión de la pasarela por la operación |
| `monto_neto` | entero | Lo que la pasarela paga por la operación: bruto menos comisión |
| `iva_comision` | entero | IVA de la comisión de la pasarela, informado por separado |
| `monto_liquidado` | entero | Lo que la pasarela paga por la operación, después de comisión e IVA |

Nota del proveedor: "a partir de la versión 2 del reporte, el IVA de la comisión se informa en su propia columna". La pasarela no avisó la fecha del cambio.

## 3. `banco/extracto_AAAAMMDD.csv`

Cartola diaria de la cuenta corriente de Pagoflux, tal como la descarga Tesorería del portal del banco. Solo días hábiles bancarios. **CSV con separador `;`, codificación Latin-1 (ISO-8859-1), miles con `.`, sin decimales.**

| Campo | Tipo | Significado de negocio |
|---|---|---|
| `Fecha` | fecha `DD/MM/AAAA` | Fecha contable del movimiento en el banco |
| `Fecha Valor` | fecha `DD/MM/AAAA` | Fecha en que el banco considera disponible el dinero |
| `Descripción` | texto | Glosa del banco (texto libre del banco: transferencias, abonos de la pasarela, comisiones del banco, devoluciones) |
| `N° Documento` | texto | Número de documento o referencia asociado, cuando el banco lo informa |
| `Cargos` | entero con separador de miles | Salida de dinero |
| `Abonos` | entero con separador de miles | Entrada de dinero |
| `Saldo` | entero con separador de miles | Saldo de la cuenta después del movimiento |

## 4. `maestros/comercios/comercios_AAAA-MM-DD.csv`

Foto completa de la cartera de comercios al cierre de cada día, exportada por el área comercial. CSV, UTF-8.

| Campo | Tipo | Significado de negocio |
|---|---|---|
| `id_comercio` | texto | Identificador del comercio |
| `rut` | texto | RUT de la empresa del comercio |
| `razon_social` | texto | Nombre legal |
| `rubro` | texto | Rubro comercial |
| `plan` | texto | Plan contratado: `BASICO`, `PRO`, `ENTERPRISE` |
| `tasa_comision_pct` | decimal | Porcentaje de comisión (IVA incluido) que Pagoflux cobra por cada pago, según el plan vigente |
| `estado` | texto | `ACTIVO` o `SUSPENDIDO` (un comercio suspendido no puede recibir pagos nuevos) |
| `fecha_alta` | fecha | Fecha de alta del comercio |
| `actualizado_en` | timestamp UTC | Último cambio del registro en el sistema comercial |

## 5. `maestros/plan_cuentas.csv`

Plan de cuentas que entrega Contabilidad.

| Campo | Tipo | Significado de negocio |
|---|---|---|
| `codigo_cuenta` | texto | Código de la cuenta contable |
| `nombre` | texto | Nombre de la cuenta |
| `tipo` | texto | `ACTIVO`, `PASIVO`, `PATRIMONIO`, `INGRESO`, `GASTO` |
| `naturaleza` | texto | `DEUDORA` (aumenta con débitos) o `ACREEDORA` (aumenta con créditos) |
| `descripcion` | texto | Para qué se usa la cuenta, en palabras de Contabilidad |

## 6. `maestros/tipo_cambio.csv`

Tipo de cambio oficial que usa Contabilidad. Solo se publica en días hábiles.

| Campo | Tipo | Significado de negocio |
|---|---|---|
| `fecha` | fecha | Día de publicación |
| `moneda` | texto | `USD` |
| `valor_clp` | decimal | Pesos por dólar |

## 7. `maestros/feriados.csv`

Feriados bancarios (días sin extracto, sin liquidación de la pasarela y sin dispersiones).

| Campo | Tipo | Significado de negocio |
|---|---|---|
| `fecha` | fecha | Día feriado |
| `descripcion` | texto | Descripción |

---

## Reglas de negocio que informa el cliente

- La pasarela paga cada captura uno o dos días hábiles después de la operación.
- Las transferencias de compradores llegan al banco el mismo día hábil si se hacen antes de las 18:00 (hora de Santiago); si no, el día hábil siguiente.
- Pagoflux le transfiere a cada comercio, cada día hábil a media mañana, lo acumulado hasta el día anterior (pagos aprobados menos comisiones y reembolsos), cuando el saldo es positivo.
- El IVA vigente es 19 %.

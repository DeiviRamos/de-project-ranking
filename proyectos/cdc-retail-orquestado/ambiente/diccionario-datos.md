# Diccionario de datos — base transaccional "tienda" (Casa Brisa, sintética)

Base PostgreSQL, esquema `tienda`. Todos los datos son sintéticos. Las marcas de tiempo son `timestamptz`.

## clientes
Personas registradas en la tienda.
| Campo | Tipo | Significado |
|---|---|---|
| cliente_id | bigserial PK | Identificador interno del cliente |
| nombre | text, no nulo | Nombre completo |
| email | text | Correo de contacto |
| telefono | text | Teléfono de contacto |
| ciudad | text | Ciudad de entrega habitual |
| pais | char(2) | País (código ISO) |
| creado_en | timestamptz | Fecha de alta |
| updated_at | timestamptz | Última modificación del registro |

## productos
Catálogo vendible.
| Campo | Tipo | Significado |
|---|---|---|
| producto_id | bigserial PK | Identificador interno |
| sku | text, único | Código comercial del producto |
| nombre | text | Nombre comercial |
| categoria | text | Categoría de catálogo |
| precio | numeric | Precio de lista vigente, en moneda local |
| activo | boolean | Si se ofrece actualmente |
| updated_at | timestamptz | Última modificación |

## inventario
Existencias por producto (una fila por producto).
| Campo | Tipo | Significado |
|---|---|---|
| producto_id | bigint PK/FK → productos | Producto |
| cantidad | integer ≥ 0 | Unidades disponibles |
| updated_at | timestamptz | Última actualización |

## pedidos
Encabezado de compra.
| Campo | Tipo | Significado |
|---|---|---|
| pedido_id | bigserial PK | Identificador del pedido |
| cliente_id | bigint FK → clientes | Quien compra |
| estado | text | Etapa del pedido: `creado`, `pagado`, `enviado`, `entregado`, `cancelado` |
| total | numeric | Importe total del pedido registrado por la tienda |
| creado_en | timestamptz | Momento en que se creó |
| updated_at | timestamptz | Última modificación |

## pedido_items
Partidas de un pedido.
| Campo | Tipo | Significado |
|---|---|---|
| item_id | bigserial PK | Identificador de la partida |
| pedido_id | bigint FK → pedidos | Pedido al que pertenece |
| producto_id | bigint FK → productos | Producto vendido |
| cantidad | integer > 0 | Unidades |
| precio_unitario | numeric | Precio aplicado al momento de la venta |

## pagos
Cobros registrados contra un pedido.
| Campo | Tipo | Significado |
|---|---|---|
| pago_id | bigserial PK | Identificador del pago |
| pedido_id | bigint FK → pedidos | Pedido pagado |
| metodo | text | Medio de pago (`tarjeta`, `transferencia`, `efectivo_contra_entrega`, `billetera`) |
| monto | numeric | Importe cobrado |
| pagado_en | timestamptz | Momento del cobro |

## Objetos de replicación disponibles
Publicación `cdc_publication` (todas las tablas) y rol de replicación definido por `CDC_USER`/`CDC_PASSWORD` en `.env`.

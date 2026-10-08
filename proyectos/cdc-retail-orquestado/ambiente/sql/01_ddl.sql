-- Esquema transaccional fuente: tienda en línea simulada (datos sintéticos).
CREATE SCHEMA IF NOT EXISTS tienda;
SET search_path TO tienda;

CREATE TABLE clientes (
    cliente_id      BIGSERIAL PRIMARY KEY,
    nombre          TEXT        NOT NULL,
    email           TEXT,
    telefono        TEXT,
    ciudad          TEXT,
    pais            CHAR(2)     NOT NULL DEFAULT 'MX',
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE productos (
    producto_id     BIGSERIAL PRIMARY KEY,
    sku             TEXT        NOT NULL UNIQUE,
    nombre          TEXT        NOT NULL,
    categoria       TEXT        NOT NULL,
    precio          NUMERIC(10,2) NOT NULL CHECK (precio >= 0),
    activo          BOOLEAN     NOT NULL DEFAULT TRUE,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE inventario (
    producto_id     BIGINT PRIMARY KEY REFERENCES productos(producto_id) ON DELETE CASCADE,
    cantidad        INTEGER     NOT NULL CHECK (cantidad >= 0),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE pedidos (
    pedido_id       BIGSERIAL PRIMARY KEY,
    cliente_id      BIGINT      NOT NULL REFERENCES clientes(cliente_id),
    estado          TEXT        NOT NULL,
    total           NUMERIC(12,2) NOT NULL DEFAULT 0,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE pedido_items (
    item_id         BIGSERIAL PRIMARY KEY,
    pedido_id       BIGINT      NOT NULL REFERENCES pedidos(pedido_id) ON DELETE CASCADE,
    producto_id     BIGINT      NOT NULL REFERENCES productos(producto_id),
    cantidad        INTEGER     NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL
);

CREATE TABLE pagos (
    pago_id         BIGSERIAL PRIMARY KEY,
    pedido_id       BIGINT      NOT NULL REFERENCES pedidos(pedido_id) ON DELETE CASCADE,
    metodo          TEXT        NOT NULL,
    monto           NUMERIC(12,2) NOT NULL,
    pagado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ON pedidos (cliente_id);
CREATE INDEX ON pedido_items (pedido_id);
CREATE INDEX ON pagos (pedido_id);

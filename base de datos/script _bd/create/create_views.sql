-- Vista de movimientos con información de usuario y producto
CREATE OR REPLACE VIEW vista_movimientos_detalle AS
SELECT
    m.id_movimiento,
    m.codigo,
    m.monto,
    m.cuotas,
    m.nota,
    m.fecha_creacion,
    p.nombre AS persona,
    pr.nombre AS producto,
    c.nombre AS categoria,
    b.nombre AS beneficiario,
    tm.nombre AS tipo_movimiento,
    em.nombre AS estado
FROM
    movimiento m
    JOIN persona p ON m.id_persona = p.id_persona
    JOIN producto pr ON m.id_producto = pr.id_producto
    JOIN categoria c ON m.id_categoria = c.id_categoria
    JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
    JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
    JOIN estado_movimiento em ON m.id_estado = em.id_estado;
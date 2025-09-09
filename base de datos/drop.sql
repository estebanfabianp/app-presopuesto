-- Elimina las tablas si existen antes de crearlas (orden correcto por dependencias)
DROP TABLE IF EXISTS fondo;

DROP TABLE IF EXISTS accion;

DROP TABLE IF EXISTS parametro_dian;

DROP TABLE IF EXISTS pago_tarjeta;

DROP TABLE IF EXISTS tarjeta_credito;

DROP TABLE IF EXISTS presupuesto_categoria;

DROP TABLE IF EXISTS presupuesto;

DROP TABLE IF EXISTS activo;

DROP TABLE IF EXISTS prestamo;

DROP TABLE IF EXISTS transaccion_programada;

DROP TABLE IF EXISTS movimiento;

DROP TABLE IF EXISTS beneficiario;

DROP TABLE IF EXISTS categoria;

DROP TABLE IF EXISTS producto;

DROP TABLE IF EXISTS persona;

DROP TABLE IF EXISTS tipo_movimiento;

DROP TABLE IF EXISTS tipo_producto;

DROP TABLE IF EXISTS estado_movimiento;

DROP TABLE IF EXISTS estado_prestamo;

DROP TABLE IF EXISTS estado_tarjeta;

DROP TABLE IF EXISTS frecuencia_transaccion;
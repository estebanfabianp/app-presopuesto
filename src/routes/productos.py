"""Rutas API de Productos Financieros.

Gestiona los 5 tipos de producto:
  - cuenta       → tabla `cuenta`        (ahorro, corriente, efectivo, digital)
  - tarjeta      → tabla `tarjeta_credito`
  - fondo        → tabla `accion`  (se reutiliza para fondos de inversión)
  - accion       → tabla `accion`  (acciones bursátiles)
  - activo       → tabla `activo`

Todos los endpoints requieren JWT.  El id_persona proviene del token.
"""

import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from src.database.db_connector import DatabaseConnector

bp = Blueprint('productos', __name__, url_prefix='/api/productos')
logger = logging.getLogger(__name__)

TIPOS_CUENTA = ('ahorro', 'corriente', 'efectivo', 'digital')
TIPOS_ACCION = ('accion', 'fondo')   # mercado distingue fondos de acciones


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _persona_id():
    return int(get_jwt_identity())


def _fmt(v):
    """Convierte Decimal/date a str serializable."""
    if v is None:
        return None
    if hasattr(v, 'isoformat'):
        return v.isoformat()
    return v


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/productos  — resumen unificado
# ──────────────────────────────────────────────────────────────────────────────
@bp.route('', methods=['GET'])
def list_productos():
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        solo_activos = request.args.get('solo_activos', 'false').lower() == 'true'

        # ── Cuentas (desde tabla directa) ─────────────────────────────────────
        cuentas = db.execute_query(
            """SELECT id_cuenta AS id, nombre, tipo, saldo_inicial, moneda, estado, fecha_creacion
               FROM cuenta WHERE id_persona = %s ORDER BY nombre""",
            (persona_id,),
        ) or []

        # Nota: el filtro por tipo_producto se hace en Python para evitar
        # conflictos de collation en algunos entornos MySQL.
        productos_unificados = db.execute_query(
            """SELECT v.id_producto AS id, v.tipo_producto, v.nombre,
                      t.numero_tarjeta, v.limite_credito, v.saldo_actual,
                     t.nombre_titular, t.banco, t.tipo_tarjeta,
                     t.fecha_vencimiento, t.fecha_corte, t.fecha_pago, t.fecha_creacion,
                     t.estado AS estado_tarjeta,
                      v.estado
               FROM v_producto_unificado v
               LEFT JOIN tarjeta_credito t ON t.id_tarjeta = v.id_producto
               WHERE v.id_persona = %s
               ORDER BY v.tipo_producto, v.nombre""",
            (persona_id,),
        ) or []

        tarjetas = [r for r in productos_unificados if str(r.get('tipo_producto', '')).lower() == 'tarjeta_credito']

        # ── Acciones / Fondos ─────────────────────────────────────────────────
        acciones = db.execute_query(
            """SELECT id_accion AS id, simbolo, empresa, cantidad,
                      precio_compra, precio_actual, fecha_compra, mercado, estado
               FROM accion WHERE id_persona = %s ORDER BY empresa""",
            (persona_id,),
        ) or []

        # ── Activos ───────────────────────────────────────────────────────────
        activos = db.execute_query(
            """SELECT id_activo AS id, nombre_activo AS nombre, valor,
                      depreciacion, estado, fecha_creacion
               FROM activo WHERE id_persona = %s ORDER BY nombre_activo""",
            (persona_id,),
        ) or []

        prestamos = [r for r in productos_unificados if str(r.get('tipo_producto', '')).lower() == 'prestamo']

        def filtrar(lista):
            if solo_activos:
                return [
                    r for r in lista
                    if str(r.get('estado_tarjeta') or r.get('estado', '')).upper() in ('ACTIVO', 'ACTIVA')
                ]
            return lista

        resultado = {
            'cuentas':  [_serializar_cuenta(r)  for r in filtrar(cuentas)],
            'tarjetas': [_serializar_tarjeta(r) for r in filtrar(tarjetas)],
            'acciones': [_serializar_accion(r)  for r in filtrar(acciones) if r.get('mercado', '').upper() != 'FONDO'],
            'fondos':   [_serializar_accion(r)  for r in filtrar(acciones) if r.get('mercado', '').upper() == 'FONDO'],
            'activos':  [_serializar_activo(r)  for r in filtrar(activos)],
            'prestamos': [_serializar_prestamo(r) for r in filtrar(prestamos)],
        }

        monto_cuentas = sum(float(x.get('saldo_inicial') or 0) for x in resultado['cuentas'])
        monto_activos = sum(float(x.get('valor') or 0) for x in resultado['activos'])
        monto_acciones = sum(float(x.get('valor_total') or 0) for x in resultado['acciones'])
        monto_fondos = sum(float(x.get('valor_total') or 0) for x in resultado['fondos'])
        deuda_tarjetas = sum(float(x.get('saldo_actual') or 0) for x in resultado['tarjetas'])
        deuda_prestamos = sum(float(x.get('saldo_actual') or 0) for x in resultado['prestamos'])
        activos_totales = monto_cuentas + monto_activos + monto_acciones + monto_fondos
        deuda_total = deuda_tarjetas + deuda_prestamos
        patrimonio_neto = activos_totales - deuda_total

        resultado['resumen'] = {
            'total_cuentas':  len(resultado['cuentas']),
            'total_tarjetas': len(resultado['tarjetas']),
            'total_acciones': len(resultado['acciones']),
            'total_fondos':   len(resultado['fondos']),
            'total_activos':  len(resultado['activos']),
            'total_prestamos': len(resultado['prestamos']),
            'activos_totales': round(activos_totales, 2),
            'deuda_total': round(deuda_total, 2),
            'patrimonio_neto': round(patrimonio_neto, 2),
        }

        return jsonify(resultado), 200
    except Exception as e:
        logger.error('Error listando productos: %s', e)
        return jsonify({'message': 'Error al listar productos', 'error': str(e)}), 500
    finally:
        db.close()


def _serializar_cuenta(r):
    return {
        'id': r['id'], 'nombre': r['nombre'], 'tipo': r['tipo'],
        'saldo_inicial': float(r['saldo_inicial'] or 0),
        'moneda': r['moneda'], 'estado': r['estado'],
        'fecha_creacion': _fmt(r.get('fecha_creacion')),
    }

def _serializar_tarjeta(r):
    return {
        'id': r['id'], 'nombre': r.get('nombre') or f"Tarjeta {r.get('numero_tarjeta','')[-4:]}",
        'numero_tarjeta': r.get('numero_tarjeta'),
        'nombre_titular': r.get('nombre_titular'),
        'banco': r.get('banco'),
        'tipo_tarjeta': r.get('tipo_tarjeta') or 'credito',
        'limite_credito': float(r['limite_credito'] or 0),
        'saldo_actual': float(r['saldo_actual'] or 0),
        'fecha_vencimiento': _fmt(r.get('fecha_vencimiento')),
        'fecha_corte': _fmt(r.get('fecha_corte')),
        'fecha_pago': _fmt(r.get('fecha_pago')),
        'estado': r.get('estado_tarjeta') or r['estado'],
        'fecha_creacion': _fmt(r.get('fecha_creacion')),
    }

def _serializar_accion(r):
    compra = float(r['precio_compra'] or 0)
    actual = float(r['precio_actual'] or compra)
    cant   = int(r['cantidad'] or 0)
    return {
        'id': r['id'], 'simbolo': r['simbolo'], 'empresa': r['empresa'],
        'cantidad': cant,
        'precio_compra': compra, 'precio_actual': actual,
        'valor_total': round(cant * actual, 2),
        'ganancia': round((actual - compra) * cant, 2),
        'fecha_compra': _fmt(r.get('fecha_compra')),
        'mercado': r['mercado'], 'estado': r['estado'],
    }

def _serializar_activo(r):
    return {
        'id': r['id'], 'nombre': r['nombre'],
        'valor': float(r['valor'] or 0),
        'depreciacion': float(r['depreciacion'] or 0),
        'estado': r['estado'],
        'fecha_creacion': _fmt(r.get('fecha_creacion')),
    }


def _serializar_prestamo(r):
    return {
        'id': r['id'],
        'nombre': r.get('nombre') or f"Préstamo #{r.get('id')}",
        'saldo_actual': float(r.get('saldo_actual') or 0),
        'estado': r.get('estado') or 'ACTIVO',
    }


# ──────────────────────────────────────────────────────────────────────────────
# CRUD Cuentas
# ──────────────────────────────────────────────────────────────────────────────
@bp.route('/cuentas', methods=['POST'])
def create_cuenta():
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        d = request.get_json() or {}
        nombre = (d.get('nombre') or '').strip()
        tipo   = (d.get('tipo') or 'ahorro').strip().lower()
        saldo  = float(d.get('saldo_inicial') or 0)
        moneda = (d.get('moneda') or 'COP').strip().upper()

        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400
        if tipo not in TIPOS_CUENTA:
            return jsonify({'message': f'tipo debe ser: {", ".join(TIPOS_CUENTA)}'}), 400

        db.execute_non_query(
            "INSERT INTO cuenta (id_persona, nombre, tipo, saldo_inicial, moneda, estado) VALUES (%s,%s,%s,%s,%s,'ACTIVO')",
            (persona_id, nombre, tipo, saldo, moneda),
        )
        return jsonify({'message': 'Cuenta creada'}), 201
    except Exception as e:
        logger.error('Error creando cuenta: %s', e)
        return jsonify({'message': 'Error al crear cuenta'}), 500
    finally:
        db.close()


@bp.route('/cuentas/<int:cuenta_id>', methods=['PUT'])
def update_cuenta(cuenta_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT id_cuenta FROM cuenta WHERE id_cuenta=%s AND id_persona=%s LIMIT 1",
            (cuenta_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Cuenta no encontrada'}), 404
        d = request.get_json() or {}
        nombre = (d.get('nombre') or '').strip()
        tipo   = (d.get('tipo') or 'ahorro').strip().lower()
        saldo  = float(d.get('saldo_inicial') or 0)
        moneda = (d.get('moneda') or 'COP').strip().upper()
        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400
        if tipo not in TIPOS_CUENTA:
            return jsonify({'message': f'tipo debe ser: {", ".join(TIPOS_CUENTA)}'}), 400
        db.execute_non_query(
            "UPDATE cuenta SET nombre=%s, tipo=%s, saldo_inicial=%s, moneda=%s WHERE id_cuenta=%s",
            (nombre, tipo, saldo, moneda, cuenta_id),
        )
        return jsonify({'message': 'Cuenta actualizada'}), 200
    except Exception as e:
        logger.error('Error actualizando cuenta %s: %s', cuenta_id, e)
        return jsonify({'message': 'Error al actualizar cuenta'}), 500
    finally:
        db.close()


@bp.route('/cuentas/<int:cuenta_id>/estado', methods=['PATCH'])
def toggle_cuenta(cuenta_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT estado FROM cuenta WHERE id_cuenta=%s AND id_persona=%s LIMIT 1",
            (cuenta_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Cuenta no encontrada'}), 404
        nuevo = 'INACTIVO' if row[0]['estado'] == 'ACTIVO' else 'ACTIVO'
        db.execute_non_query("UPDATE cuenta SET estado=%s WHERE id_cuenta=%s", (nuevo, cuenta_id))
        return jsonify({'message': 'Estado actualizado', 'estado': nuevo}), 200
    except Exception as e:
        logger.error('Error toggle cuenta %s: %s', cuenta_id, e)
        return jsonify({'message': 'Error al cambiar estado'}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# CRUD Acciones / Fondos  (misma tabla, mercado distingue)
# ──────────────────────────────────────────────────────────────────────────────
@bp.route('/acciones', methods=['POST'])
def create_accion():
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        d = request.get_json() or {}
        simbolo  = (d.get('simbolo') or '').strip().upper()
        empresa  = (d.get('empresa') or '').strip()
        cantidad = int(d.get('cantidad') or 0)
        precio_c = float(d.get('precio_compra') or 0)
        precio_a = float(d.get('precio_actual') or precio_c)
        fecha_c  = d.get('fecha_compra') or None
        mercado  = (d.get('mercado') or 'NYSE').strip().upper()

        if not empresa:
            return jsonify({'message': 'El nombre/empresa es obligatorio'}), 400

        db.execute_non_query(
            """INSERT INTO accion (simbolo, empresa, cantidad, precio_compra, precio_actual,
               fecha_compra, mercado, id_persona, estado)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVO')""",
            (simbolo, empresa, cantidad, precio_c, precio_a, fecha_c, mercado, persona_id),
        )
        return jsonify({'message': 'Acción/Fondo creado'}), 201
    except Exception as e:
        logger.error('Error creando accion: %s', e)
        return jsonify({'message': 'Error al crear acción/fondo'}), 500
    finally:
        db.close()


@bp.route('/acciones/<int:accion_id>', methods=['PUT'])
def update_accion(accion_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT id_accion FROM accion WHERE id_accion=%s AND id_persona=%s LIMIT 1",
            (accion_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Acción no encontrada'}), 404
        d = request.get_json() or {}
        simbolo  = (d.get('simbolo') or '').strip().upper()
        empresa  = (d.get('empresa') or '').strip()
        cantidad = int(d.get('cantidad') or 0)
        precio_c = float(d.get('precio_compra') or 0)
        precio_a = float(d.get('precio_actual') or precio_c)
        fecha_c  = d.get('fecha_compra') or None
        mercado  = (d.get('mercado') or 'NYSE').strip().upper()
        if not empresa:
            return jsonify({'message': 'El nombre/empresa es obligatorio'}), 400
        db.execute_non_query(
            """UPDATE accion SET simbolo=%s, empresa=%s, cantidad=%s,
               precio_compra=%s, precio_actual=%s, fecha_compra=%s, mercado=%s
               WHERE id_accion=%s""",
            (simbolo, empresa, cantidad, precio_c, precio_a, fecha_c, mercado, accion_id),
        )
        return jsonify({'message': 'Acción/Fondo actualizado'}), 200
    except Exception as e:
        logger.error('Error actualizando accion %s: %s', accion_id, e)
        return jsonify({'message': 'Error al actualizar acción/fondo'}), 500
    finally:
        db.close()


@bp.route('/acciones/<int:accion_id>/estado', methods=['PATCH'])
def toggle_accion(accion_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT estado FROM accion WHERE id_accion=%s AND id_persona=%s LIMIT 1",
            (accion_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Acción no encontrada'}), 404
        nuevo = 'INACTIVO' if row[0]['estado'] == 'ACTIVO' else 'ACTIVO'
        db.execute_non_query("UPDATE accion SET estado=%s WHERE id_accion=%s", (nuevo, accion_id))
        return jsonify({'message': 'Estado actualizado', 'estado': nuevo}), 200
    except Exception as e:
        logger.error('Error toggle accion %s: %s', accion_id, e)
        return jsonify({'message': 'Error al cambiar estado'}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# CRUD Activos
# ──────────────────────────────────────────────────────────────────────────────
@bp.route('/activos', methods=['POST'])
def create_activo():
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        d = request.get_json() or {}
        nombre = (d.get('nombre') or '').strip()
        valor  = float(d.get('valor') or 0)
        depreciacion = float(d.get('depreciacion') or 0)
        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400
        db.execute_non_query(
            "INSERT INTO activo (nombre_activo, valor, depreciacion, id_persona, estado) VALUES (%s,%s,%s,%s,'ACTIVO')",
            (nombre, valor, depreciacion, persona_id),
        )
        return jsonify({'message': 'Activo creado'}), 201
    except Exception as e:
        logger.error('Error creando activo: %s', e)
        return jsonify({'message': 'Error al crear activo'}), 500
    finally:
        db.close()




# ──────────────────────────────────────────────────────────────────────────────
# CRUD Tarjetas de Crédito
# ──────────────────────────────────────────────────────────────────────────────
@bp.route('/tarjetas', methods=['POST'])
def create_tarjeta():
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        d = request.get_json() or {}
        numero_tarjeta = (d.get('numero_tarjeta') or '').strip().replace(' ', '')
        nombre_titular = (d.get('nombre_titular') or '').strip()
        banco = (d.get('banco') or '').strip()
        tipo_tarjeta = (d.get('tipo_tarjeta') or 'credito').strip().lower()
        limite_credito = float(d.get('limite_credito') or 0)
        saldo_actual = float(d.get('saldo_actual') or 0)
        fecha_vencimiento = d.get('fecha_vencimiento') or None
        fecha_corte = d.get('fecha_corte') or None
        fecha_pago = d.get('fecha_pago') or None
        estado = (d.get('estado') or 'activa').strip().lower()

        # Validaciones
        if not numero_tarjeta or len(numero_tarjeta) != 16 or not numero_tarjeta.isdigit():
            return jsonify({'message': 'El número de tarjeta debe tener 16 dígitos'}), 400
        if not nombre_titular:
            return jsonify({'message': 'El nombre del titular es obligatorio'}), 400

        db.execute_non_query(
            """INSERT INTO tarjeta_credito (numero_tarjeta, nombre_titular, banco, tipo_tarjeta,
                    limite_credito, saldo_actual, fecha_vencimiento, fecha_corte, fecha_pago, estado, id_persona)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (numero_tarjeta, nombre_titular, banco, tipo_tarjeta, limite_credito, saldo_actual,
                 fecha_vencimiento, fecha_corte, fecha_pago, estado, persona_id),
        )
        return jsonify({'message': 'Tarjeta creada', 'status': 'success'}), 201
    except Exception as e:
        logger.error('Error creando tarjeta: %s', e)
        return jsonify({'message': 'Error al crear tarjeta', 'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/tarjetas/<int:tarjeta_id>', methods=['PUT'])
def update_tarjeta(tarjeta_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT id_tarjeta FROM tarjeta_credito WHERE id_tarjeta=%s AND (id_persona=%s OR id_persona IS NULL) LIMIT 1",
            (tarjeta_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Tarjeta no encontrada'}), 404

        d = request.get_json() or {}
        numero_tarjeta = (d.get('numero_tarjeta') or '').strip().replace(' ', '')
        nombre_titular = (d.get('nombre_titular') or '').strip()
        banco = (d.get('banco') or '').strip()
        tipo_tarjeta = (d.get('tipo_tarjeta') or 'credito').strip().lower()
        limite_credito = float(d.get('limite_credito') or 0)
        saldo_actual = float(d.get('saldo_actual') or 0)
        fecha_vencimiento = d.get('fecha_vencimiento') or None
        fecha_corte = d.get('fecha_corte') or None
        fecha_pago = d.get('fecha_pago') or None
        estado = (d.get('estado') or 'activa').strip().lower()

        # Validaciones
        if not numero_tarjeta or len(numero_tarjeta) != 16 or not numero_tarjeta.isdigit():
            return jsonify({'message': 'El número de tarjeta debe tener 16 dígitos'}), 400
        if not nombre_titular:
            return jsonify({'message': 'El nombre del titular es obligatorio'}), 400

        db.execute_non_query(
            """UPDATE tarjeta_credito SET numero_tarjeta=%s, nombre_titular=%s, banco=%s,
                    tipo_tarjeta=%s, limite_credito=%s, saldo_actual=%s, fecha_vencimiento=%s,
                          fecha_corte=%s, fecha_pago=%s, estado=%s, id_persona=%s
               WHERE id_tarjeta=%s""",
            (numero_tarjeta, nombre_titular, banco, tipo_tarjeta, limite_credito, saldo_actual,
                      fecha_vencimiento, fecha_corte, fecha_pago, estado, persona_id, tarjeta_id),
        )
        return jsonify({'message': 'Tarjeta actualizada', 'status': 'success'}), 200
    except Exception as e:
        logger.error('Error actualizando tarjeta %s: %s', tarjeta_id, e)
        return jsonify({'message': 'Error al actualizar tarjeta', 'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/tarjetas/<int:tarjeta_id>/estado', methods=['PATCH'])
def toggle_tarjeta(tarjeta_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT estado FROM tarjeta_credito WHERE id_tarjeta=%s AND (id_persona=%s OR id_persona IS NULL) LIMIT 1",
            (tarjeta_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Tarjeta no encontrada'}), 404
        nuevo = 'inactiva' if row[0]['estado'].lower() == 'activa' else 'activa'
        db.execute_non_query("UPDATE tarjeta_credito SET estado=%s WHERE id_tarjeta=%s", (nuevo, tarjeta_id))
        return jsonify({'message': 'Estado actualizado', 'estado': nuevo, 'status': 'success'}), 200
    except Exception as e:
        logger.error('Error toggle tarjeta %s: %s', tarjeta_id, e)
        return jsonify({'message': 'Error al cambiar estado'}), 500
    finally:
        db.close()


@bp.route('/activos/<int:activo_id>', methods=['PUT'])
def update_activo(activo_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT id_activo FROM activo WHERE id_activo=%s AND id_persona=%s LIMIT 1",
            (activo_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Activo no encontrado'}), 404
        d = request.get_json() or {}
        nombre = (d.get('nombre') or '').strip()
        valor  = float(d.get('valor') or 0)
        depreciacion = float(d.get('depreciacion') or 0)
        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400
        db.execute_non_query(
            "UPDATE activo SET nombre_activo=%s, valor=%s, depreciacion=%s WHERE id_activo=%s",
            (nombre, valor, depreciacion, activo_id),
        )
        return jsonify({'message': 'Activo actualizado'}), 200
    except Exception as e:
        logger.error('Error actualizando activo %s: %s', activo_id, e)
        return jsonify({'message': 'Error al actualizar activo'}), 500
    finally:
        db.close()


@bp.route('/activos/<int:activo_id>/estado', methods=['PATCH'])
def toggle_activo(activo_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT estado FROM activo WHERE id_activo=%s AND id_persona=%s LIMIT 1",
            (activo_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Activo no encontrado'}), 404
        nuevo = 'INACTIVO' if row[0]['estado'] == 'ACTIVO' else 'ACTIVO'
        db.execute_non_query("UPDATE activo SET estado=%s WHERE id_activo=%s", (nuevo, activo_id))
        return jsonify({'message': 'Estado actualizado', 'estado': nuevo}), 200
    except Exception as e:
        logger.error('Error toggle activo %s: %s', activo_id, e)
        return jsonify({'message': 'Error al cambiar estado'}), 500
    finally:
        db.close()


@bp.route('/prestamos/<int:prestamo_id>/estado', methods=['PATCH'])
def toggle_prestamo(prestamo_id):
    verify_jwt_in_request()
    persona_id = _persona_id()
    db = DatabaseConnector()
    try:
        row = db.execute_query(
            "SELECT id_estado FROM prestamo WHERE id_prestamo=%s AND id_persona=%s LIMIT 1",
            (prestamo_id, persona_id),
        )
        if not row:
            return jsonify({'message': 'Préstamo no encontrado'}), 404

        # Garantiza existencia de estado inactivo en catálogo.
        inactivo = db.execute_query(
            "SELECT id_estado FROM estado_prestamo WHERE LOWER(nombre)='inactivo' LIMIT 1"
        )
        if inactivo:
            id_inactivo = int(inactivo[0]['id_estado'])
        else:
            db.execute_non_query("INSERT INTO estado_prestamo (nombre) VALUES ('inactivo')")
            inactivo = db.execute_query(
                "SELECT id_estado FROM estado_prestamo WHERE LOWER(nombre)='inactivo' LIMIT 1"
            )
            id_inactivo = int(inactivo[0]['id_estado'])

        activo = db.execute_query(
            "SELECT id_estado FROM estado_prestamo WHERE LOWER(nombre)='activo' LIMIT 1"
        )
        id_activo = int(activo[0]['id_estado']) if activo else 1

        actual = int(row[0]['id_estado'] or id_activo)
        nuevo = id_inactivo if actual == id_activo else id_activo
        nombre_nuevo = 'INACTIVO' if nuevo == id_inactivo else 'ACTIVO'

        db.execute_non_query("UPDATE prestamo SET id_estado=%s WHERE id_prestamo=%s", (nuevo, prestamo_id))
        return jsonify({'message': 'Estado actualizado', 'estado': nombre_nuevo}), 200
    except Exception as e:
        logger.error('Error toggle prestamo %s: %s', prestamo_id, e)
        return jsonify({'message': 'Error al cambiar estado'}), 500
    finally:
        db.close()

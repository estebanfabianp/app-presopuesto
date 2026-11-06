"""Préstamos, cuotas y pagos con transacciones independientes por usuario."""

import json
import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.business.services.prestamos import calcular_plan, dinero
from src.database.db_connector import DatabaseConnector

bp = Blueprint('prestamos', __name__, url_prefix='/api/prestamos')
logger = logging.getLogger(__name__)
ZERO = Decimal('0.00')


def _usuario():
    verify_jwt_in_request()
    identidad = get_jwt_identity()
    if not str(identidad).isdigit() or int(identidad) <= 0:
        return None
    return int(identidad)


def _texto(valor, nombre, limite):
    if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > limite:
        raise ValueError(f'{nombre} es obligatorio y debe tener hasta {limite} caracteres')
    return valor.strip()


def _fecha(valor):
    try:
        return date.fromisoformat(valor)
    except (ValueError, TypeError):
        raise ValueError('La fecha no es válida') from None


def _cargos(datos):
    if not isinstance(datos, list) or len(datos) > 20:
        raise ValueError('Se permiten hasta 20 cargos por cuota')
    resultado = []
    nombres = set()
    for cargo in datos:
        if not isinstance(cargo, dict):
            raise ValueError('El cargo no es válido')
        nombre = _texto(cargo.get('nombre'), 'El nombre del cargo', 100)
        if nombre.casefold() in nombres:
            raise ValueError('Los nombres de los cargos deben ser diferentes')
        nombres.add(nombre.casefold())
        resultado.append((nombre, dinero(cargo.get('monto'))))
    return resultado


def _conexion():
    db = DatabaseConnector()
    if not db.is_connected():
        db.close()
        raise RuntimeError('No fue posible conectar con la base de datos')
    return db


def _obtener_prestamo(cursor, prestamo_id, usuario, bloquear=False):
    cursor.execute(
        'SELECT * FROM prestamo WHERE id = %s AND id_persona = %s' +
        (' FOR UPDATE' if bloquear else ''), (prestamo_id, usuario),
    )
    prestamo = cursor.fetchone()
    if not prestamo:
        raise LookupError('Préstamo no encontrado')
    return prestamo


def _cuotas(cursor, prestamo_id):
    cursor.execute('SELECT * FROM prestamo_cuota WHERE id_prestamo = %s ORDER BY numero', (prestamo_id,))
    cuotas = cursor.fetchall()
    cursor.execute(
        'SELECT c.* FROM prestamo_cargo c JOIN prestamo_cuota q ON q.id = c.id_cuota '
        'WHERE q.id_prestamo = %s ORDER BY c.id', (prestamo_id,),
    )
    cargos = cursor.fetchall()
    for cuota in cuotas:
        cuota['cargos'] = [cargo for cargo in cargos if cargo['id_cuota'] == cuota['id']]
        cuota['pendiente'] = (
            cuota['capital'] - cuota['capital_pagado'] +
            cuota['interes'] - cuota['interes_pagado'] +
            sum((c['monto'] - c['pagado'] for c in cuota['cargos']), ZERO)
        )
    return cuotas


def _saldo_capital(cursor, prestamo):
    cursor.execute('SELECT COALESCE(SUM(capital), 0) AS pagado FROM prestamo_pago WHERE id_prestamo = %s',
                   (prestamo['id'],))
    return prestamo['capital'] - cursor.fetchone()['pagado']


def _recalcular(cursor, prestamo, cuotas, saldo):
    if not cuotas:
        if saldo != 0:
            raise ValueError('La última cuota debe cubrir todo el capital pendiente')
        return
    if saldo == 0:
        cursor.executemany('UPDATE prestamo_cuota SET cancelada = 1, capital = 0, interes = 0 WHERE id = %s',
                           [(c['id'],) for c in cuotas])
        return
    plan = calcular_plan(saldo, prestamo['tasa_ea'], len(cuotas), prestamo['frecuencia'],
                         prestamo['metodo'], cuotas[0]['fecha'])
    cursor.executemany(
        'UPDATE prestamo_cuota SET capital = %s, interes = %s WHERE id = %s',
        [(item['capital'], item['interes'], cuota['id']) for item, cuota in zip(plan, cuotas)],
    )


def _respuesta_error(exc):
    if isinstance(exc, (ValueError, LookupError)):
        return jsonify({'message': str(exc)}), 404 if isinstance(exc, LookupError) else 400
    logger.exception('Error en módulo de préstamos')
    return jsonify({'message': 'No fue posible procesar el préstamo. Revisa la conexión y la migración de base de datos.'}), 500


@bp.route('', methods=['GET', 'POST'])
def prestamos():
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        db = _conexion()
        with db.conn.cursor(dictionary=True) as cursor:
            if request.method == 'GET':
                cursor.execute(
                    'SELECT p.*, p.capital - COALESCE((SELECT SUM(capital) FROM prestamo_pago '
                    'WHERE id_prestamo = p.id), 0) AS saldo FROM prestamo p '
                    'WHERE p.id_persona = %s ORDER BY p.id DESC', (usuario,),
                )
                return jsonify({'prestamos': cursor.fetchall()})

            datos = request.get_json()
            if not isinstance(datos, dict):
                raise ValueError('Datos del préstamo inválidos')
            nombre = _texto(datos.get('nombre'), 'El nombre', 120)
            acreedor = _texto(datos.get('acreedor'), 'El acreedor', 120)
            capital = dinero(datos.get('capital'))
            fecha = _fecha(datos.get('primera_fecha'))
            cargos = _cargos(datos.get('cargos', []))
            plan = calcular_plan(capital, datos.get('tasa_ea'), datos.get('numero_cuotas'),
                                 datos.get('frecuencia'), datos.get('metodo'), fecha)
            tasa = Decimal(str(datos['tasa_ea']))
            if tasa.as_tuple().exponent < -4:
                raise ValueError('La tasa admite hasta cuatro decimales')
            db.conn.start_transaction()
            cursor.execute(
                'INSERT INTO prestamo (id_persona,nombre,acreedor,capital,tasa_ea,numero_cuotas,'
                'frecuencia,metodo,primera_fecha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (usuario, nombre, acreedor, capital, tasa, len(plan),
                 datos['frecuencia'], datos['metodo'], fecha),
            )
            prestamo_id = cursor.lastrowid
            for cuota in plan:
                cursor.execute(
                    'INSERT INTO prestamo_cuota (id_prestamo,numero,fecha,capital,interes) VALUES (%s,%s,%s,%s,%s)',
                    (prestamo_id, cuota['numero'], cuota['fecha'], cuota['capital'], cuota['interes']),
                )
                cuota_id = cursor.lastrowid
                if cargos:
                    cursor.executemany('INSERT INTO prestamo_cargo (id_cuota,nombre,monto) VALUES (%s,%s,%s)',
                                       [(cuota_id, n, m) for n, m in cargos])
            db.conn.commit()
            return jsonify({'id': prestamo_id, 'message': 'Préstamo creado'}), 201
    except Exception as exc:
        if db and db.conn:
            db.conn.rollback()
        return _respuesta_error(exc)
    finally:
        if db:
            db.close()


@bp.route('/<int:prestamo_id>', methods=['GET'])
def detalle(prestamo_id):
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        db = _conexion()
        with db.conn.cursor(dictionary=True) as cursor:
            prestamo = _obtener_prestamo(cursor, prestamo_id, usuario)
            prestamo['saldo'] = _saldo_capital(cursor, prestamo)
            cuotas = _cuotas(cursor, prestamo_id)
            for cuota in cuotas:
                cuota['fecha'] = cuota['fecha'].isoformat()
            cursor.execute('SELECT * FROM prestamo_pago WHERE id_prestamo = %s ORDER BY id DESC', (prestamo_id,))
            pagos = cursor.fetchall()
            for pago in pagos:
                pago['cargos'] = json.loads(pago['cargos'])
                pago['fecha'] = pago['fecha'].isoformat()
            return jsonify({'prestamo': prestamo, 'cuotas': cuotas, 'pagos': pagos})
    except Exception as exc:
        return _respuesta_error(exc)
    finally:
        if db:
            db.close()


@bp.route('/cuentas', methods=['GET'])
def cuentas():
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        db = _conexion()
        with db.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id_cuenta, nombre, moneda FROM cuenta WHERE id_persona=%s "
                           "AND UPPER(TRIM(moneda))='COP' ORDER BY nombre",
                           (usuario,))
            return jsonify({'cuentas': cursor.fetchall()})
    except Exception as exc:
        return _respuesta_error(exc)
    finally:
        if db:
            db.close()


@bp.route('/<int:prestamo_id>/cuotas/<int:numero>', methods=['PUT'])
def ajustar_cuota(prestamo_id, numero):
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        datos = request.get_json()
        if not isinstance(datos, dict):
            raise ValueError('Datos de la cuota inválidos')
        capital, interes = dinero(datos.get('capital')), dinero(datos.get('interes'))
        cargos = _cargos(datos.get('cargos'))
        db = _conexion()
        db.conn.start_transaction()
        with db.conn.cursor(dictionary=True) as cursor:
            prestamo = _obtener_prestamo(cursor, prestamo_id, usuario, True)
            cuotas = _cuotas(cursor, prestamo_id)
            pendientes = [q for q in cuotas if not q['cancelada'] and q['pendiente'] > 0]
            actual = next((q for q in pendientes if q['numero'] == numero), None)
            if not actual:
                raise LookupError('Cuota pendiente no encontrada')
            if actual['capital_pagado'] or actual['interes_pagado'] or any(c['pagado'] for c in actual['cargos']):
                raise ValueError('No se puede ajustar una cuota que ya tiene pagos')
            if capital + interes + sum((m for _, m in cargos), ZERO) <= 0:
                raise ValueError('La cuota debe tener un importe mayor que cero')
            if actual == pendientes[0]:
                saldo = _saldo_capital(cursor, prestamo)
                if capital > saldo:
                    raise ValueError('El capital de la cuota supera el saldo pendiente')
                _recalcular(cursor, prestamo, pendientes[1:], saldo - capital)
            elif capital != actual['capital'] or interes != actual['interes']:
                raise ValueError('Solo puedes cambiar capital e interés en la próxima cuota pendiente')
            cursor.execute('UPDATE prestamo_cuota SET capital=%s, interes=%s WHERE id=%s',
                           (capital, interes, actual['id']))
            cursor.execute('DELETE FROM prestamo_cargo WHERE id_cuota=%s', (actual['id'],))
            if cargos:
                cursor.executemany('INSERT INTO prestamo_cargo (id_cuota,nombre,monto) VALUES (%s,%s,%s)',
                                   [(actual['id'], n, m) for n, m in cargos])
            db.conn.commit()
            return jsonify({'message': 'Cuota ajustada; el capital y el interés futuros se recalcularon'})
    except Exception as exc:
        if db and db.conn:
            db.conn.rollback()
        return _respuesta_error(exc)
    finally:
        if db:
            db.close()


@bp.route('/<int:prestamo_id>/pagos', methods=['POST'])
def registrar_pago(prestamo_id):
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        datos = request.get_json()
        if not isinstance(datos, dict):
            raise ValueError('Datos del pago inválidos')
        monto = dinero(datos.get('monto'))
        if monto <= 0:
            raise ValueError('El pago debe ser mayor que cero')
        fecha = _fecha(datos.get('fecha'))
        try:
            referencia = str(UUID(datos.get('referencia')))
        except (ValueError, TypeError, AttributeError):
            raise ValueError('La referencia del pago no es válida') from None
        tipo = datos.get('tipo')
        if tipo not in ('cuota', 'abono'):
            raise ValueError('El tipo de pago no es válido')
        cuenta_id = datos.get('id_cuenta')
        if cuenta_id is not None and (isinstance(cuenta_id, bool) or not isinstance(cuenta_id, int) or cuenta_id <= 0):
            raise ValueError('La cuenta no es válida')
        db = _conexion()
        db.conn.start_transaction()
        with db.conn.cursor(dictionary=True) as cursor:
            prestamo = _obtener_prestamo(cursor, prestamo_id, usuario, True)
            cursor.execute('SELECT id FROM prestamo_pago WHERE referencia=%s AND id_prestamo=%s',
                           (referencia, prestamo_id))
            if cursor.fetchone():
                db.conn.rollback()
                return jsonify({'message': 'Este pago ya fue registrado'}), 409
            cuotas = _cuotas(cursor, prestamo_id)
            pendientes = [q for q in cuotas if not q['cancelada'] and q['pendiente'] > 0]
            if not pendientes:
                raise ValueError('No hay cuotas pendientes')
            cuota = pendientes[0]
            saldo = _saldo_capital(cursor, prestamo)
            interes = ZERO
            capital = ZERO
            cargos_pagados = []
            if tipo == 'abono':
                if cuota['capital_pagado'] or cuota['interes_pagado'] or any(c['pagado'] for c in cuota['cargos']):
                    raise ValueError('Completa la cuota parcialmente pagada antes de hacer un abono extraordinario')
                if monto > saldo:
                    raise ValueError('El abono supera el capital pendiente')
                capital = monto
                _recalcular(cursor, prestamo, pendientes, saldo - monto)
                cuota_id = None
            else:
                if datos.get('numero_cuota') != cuota['numero']:
                    raise ValueError('Solo se puede pagar la primera cuota pendiente')
                if monto > cuota['pendiente']:
                    raise ValueError('El pago supera el importe pendiente de la cuota')
                resto = monto
                for cargo in cuota['cargos']:
                    aplicado = min(resto, cargo['monto'] - cargo['pagado'])
                    if aplicado:
                        cursor.execute('UPDATE prestamo_cargo SET pagado = pagado + %s WHERE id = %s',
                                       (aplicado, cargo['id']))
                        cargos_pagados.append({'nombre': cargo['nombre'], 'monto': str(aplicado)})
                        resto -= aplicado
                interes = min(resto, cuota['interes'] - cuota['interes_pagado'])
                resto -= interes
                capital = resto
                cursor.execute('UPDATE prestamo_cuota SET interes_pagado=interes_pagado+%s, '
                               'capital_pagado=capital_pagado+%s WHERE id=%s',
                               (interes, capital, cuota['id']))
                cuota_id = cuota['id']

            movimiento_id = None
            if cuenta_id is not None:
                cursor.execute("SELECT id_cuenta FROM cuenta WHERE id_cuenta=%s AND id_persona=%s "
                               "AND UPPER(TRIM(moneda))='COP'",
                               (cuenta_id, usuario))
                if not cursor.fetchone():
                    raise ValueError('La cuenta bancaria no pertenece al usuario o no está en COP')
                cursor.execute("SELECT id_tipo FROM tipo_movimiento WHERE LOWER(TRIM(nombre))='gasto' LIMIT 1")
                tipo_gasto = cursor.fetchone()
                if not tipo_gasto:
                    raise ValueError('No existe el tipo de movimiento gasto')
                cursor.execute(
                    'INSERT INTO movimiento (id_cuenta,id_tipo,monto,fecha_creacion,nota,numero_transaccion) '
                    'VALUES (%s,%s,%s,%s,%s,%s)',
                    (cuenta_id, tipo_gasto['id_tipo'], monto, fecha,
                     f"Pago préstamo: {prestamo['nombre']}", referencia),
                )
                movimiento_id = cursor.lastrowid
            cursor.execute(
                'INSERT INTO prestamo_pago (id_prestamo,id_cuota,fecha,total,capital,interes,cargos,'
                'id_movimiento,referencia) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (prestamo_id, cuota_id, fecha, monto, capital, interes,
                 json.dumps(cargos_pagados, ensure_ascii=False), movimiento_id, referencia),
            )
            db.conn.commit()
            return jsonify({'message': 'Pago registrado'}), 201
    except Exception as exc:
        if db and db.conn:
            db.conn.rollback()
        return _respuesta_error(exc)
    finally:
        if db:
            db.close()

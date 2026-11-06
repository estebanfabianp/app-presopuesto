"""Metas de ahorro y movimientos manuales, independientes de las cuentas."""

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.business.services.prestamos import dinero
from src.database.db_connector import DatabaseConnector

logger = logging.getLogger(__name__)
bp = Blueprint('metas', __name__, url_prefix='/api/metas')


def _usuario():
    verify_jwt_in_request()
    identidad = get_jwt_identity()
    return int(identidad) if str(identidad).isdigit() and int(identidad) > 0 else None


def _conexion():
    db = DatabaseConnector()
    if not db.is_connected():
        db.close()
        raise RuntimeError('No hay conexión con la base de datos')
    return db


def _referencia(valor):
    try:
        return str(UUID(valor))
    except (ValueError, TypeError, AttributeError):
        raise ValueError('La referencia de operación no es válida') from None


def _datos_meta(datos):
    if not isinstance(datos, dict):
        raise ValueError('Los datos de la meta no son válidos')
    nombre = datos.get('nombre')
    if not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 120:
        raise ValueError('El nombre es obligatorio y admite hasta 120 caracteres')
    objetivo = dinero(datos.get('objetivo'))
    if objetivo <= 0:
        raise ValueError('El objetivo debe ser mayor que cero')
    fecha = datos.get('fecha_objetivo')
    if fecha:
        try:
            fecha = date.fromisoformat(fecha)
        except (ValueError, TypeError):
            raise ValueError('La fecha objetivo no es válida') from None
    else:
        fecha = None
    return nombre.strip(), objetivo, fecha


def _meta(cursor, meta_id, usuario, bloquear=False):
    cursor.execute(
        'SELECT * FROM meta_ahorro WHERE id=%s AND id_persona=%s' +
        (' FOR UPDATE' if bloquear else ''), (meta_id, usuario),
    )
    meta = cursor.fetchone()
    if not meta:
        raise LookupError('Meta no encontrada')
    return meta


def _formato_meta(meta):
    ahorrado = meta['ahorrado']
    objetivo = meta['objetivo']
    meta['fecha_objetivo'] = meta['fecha_objetivo'].isoformat() if meta['fecha_objetivo'] else None
    meta.pop('fecha_creacion', None)
    meta.pop('referencia', None)
    meta['faltante'] = max(Decimal('0'), objetivo - ahorrado)
    meta['progreso'] = round(ahorrado / objetivo * 100, 1)
    return meta


def _error(exc):
    if isinstance(exc, (ValueError, LookupError)):
        return jsonify({'message': str(exc)}), 404 if isinstance(exc, LookupError) else 400
    logger.exception('Error en metas de ahorro')
    return jsonify({'message': 'No fue posible procesar las metas. Revisa la conexión y la migración de base de datos.'}), 500


@bp.route('', methods=['GET', 'POST'])
def metas():
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        db = _conexion()
        with db.conn.cursor(dictionary=True) as cursor:
            if request.method == 'GET':
                cursor.execute(
                    "SELECT m.*, COALESCE((SELECT SUM(CASE WHEN a.tipo='aporte' THEN a.monto "
                    "ELSE -a.monto END) FROM meta_ahorro_movimiento a WHERE a.id_meta=m.id),0) AS ahorrado "
                    "FROM meta_ahorro m WHERE m.id_persona=%s ORDER BY m.id DESC", (usuario,),
                )
                return jsonify({'metas': [_formato_meta(m) for m in cursor.fetchall()]})
            datos = request.get_json()
            nombre, objetivo, fecha = _datos_meta(datos)
            referencia = _referencia(datos.get('referencia'))
            cursor.execute('SELECT * FROM meta_ahorro WHERE referencia=%s', (referencia,))
            anterior = cursor.fetchone()
            if anterior:
                if (anterior['id_persona'], anterior['nombre'], anterior['objetivo'], anterior['fecha_objetivo']) != (usuario, nombre, objetivo, fecha):
                    raise ValueError('La referencia ya corresponde a otra operación')
                return jsonify({'id': anterior['id'], 'message': 'Meta ya registrada'}), 200
            cursor.execute('INSERT INTO meta_ahorro (id_persona,nombre,objetivo,fecha_objetivo,referencia) VALUES (%s,%s,%s,%s,%s) '
                           'ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)',
                           (usuario, nombre, objetivo, fecha, referencia))
            meta_id = cursor.lastrowid
            cursor.execute('SELECT * FROM meta_ahorro WHERE id=%s FOR UPDATE', (meta_id,))
            registrado = cursor.fetchone()
            if (registrado['id_persona'], registrado['nombre'], registrado['objetivo'], registrado['fecha_objetivo']) != (usuario, nombre, objetivo, fecha):
                raise ValueError('La referencia ya corresponde a otra operación')
            db.conn.commit()
            return jsonify({'id': meta_id, 'message': 'Meta creada'}), 201
    except Exception as exc:
        if db and db.conn:
            db.conn.rollback()
        return _error(exc)
    finally:
        if db:
            db.close()


@bp.route('/summary', methods=['GET'])
def resumen():
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        db = _conexion()
        with db.conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT m.*, COALESCE((SELECT SUM(CASE WHEN a.tipo='aporte' THEN a.monto ELSE -a.monto END) "
                "FROM meta_ahorro_movimiento a WHERE a.id_meta=m.id),0) AS ahorrado "
                "FROM meta_ahorro m WHERE m.id_persona=%s ORDER BY m.fecha_objetivo IS NULL,m.fecha_objetivo,m.id DESC",
                (usuario,),
            )
            filas = cursor.fetchall()
            objetivo = sum((m['objetivo'] for m in filas), Decimal('0'))
            ahorrado = sum((m['ahorrado'] for m in filas), Decimal('0'))
            hoy = date.today()
            return jsonify({
                'total_metas': len(filas), 'monto_total_metas': float(objetivo),
                'metas_vigentes': sum(1 for m in filas if m['ahorrado'] < m['objetivo']),
                'metas_por_vencer': sum(1 for m in filas if m['ahorrado'] < m['objetivo'] and m['fecha_objetivo'] and 0 <= (m['fecha_objetivo'] - hoy).days <= 30),
                'avance_estimado_pct': round(float(ahorrado / objetivo * 100), 2) if objetivo else 0,
                'gasto_mes': None, 'presupuesto_vigente': None,
                'metas': [{'id': m['id'], 'nombre': m['nombre'], 'monto_total': float(m['objetivo']),
                           'fecha_inicio': None, 'fecha_fin': m['fecha_objetivo'].isoformat() if m['fecha_objetivo'] else None,
                           'dias_restantes': (m['fecha_objetivo'] - hoy).days if m['fecha_objetivo'] else None}
                          for m in filas[:5]],
            })
    except Exception as exc:
        return _error(exc)
    finally:
        if db:
            db.close()


@bp.route('/<int:meta_id>', methods=['GET', 'PUT'])
def detalle(meta_id):
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        db = _conexion()
        with db.conn.cursor(dictionary=True) as cursor:
            meta = _meta(cursor, meta_id, usuario, bloquear=request.method == 'PUT')
            if request.method == 'PUT':
                nombre, objetivo, fecha = _datos_meta(request.get_json())
                cursor.execute('UPDATE meta_ahorro SET nombre=%s,objetivo=%s,fecha_objetivo=%s WHERE id=%s',
                               (nombre, objetivo, fecha, meta_id))
                db.conn.commit()
                return jsonify({'message': 'Meta actualizada'})
            cursor.execute(
                "SELECT id,tipo,monto,nota,fecha_creacion FROM meta_ahorro_movimiento "
                "WHERE id_meta=%s ORDER BY id DESC", (meta_id,),
            )
            movimientos = cursor.fetchall()
            ahorrado = sum((m['monto'] if m['tipo'] == 'aporte' else -m['monto'] for m in movimientos), Decimal('0'))
            meta['ahorrado'] = ahorrado
            for movimiento in movimientos:
                movimiento['fecha_creacion'] = movimiento['fecha_creacion'].isoformat()
            return jsonify({'meta': _formato_meta(meta), 'movimientos': movimientos})
    except Exception as exc:
        if db and db.conn:
            db.conn.rollback()
        return _error(exc)
    finally:
        if db:
            db.close()


@bp.route('/<int:meta_id>/movimientos', methods=['POST'])
def registrar_movimiento(meta_id):
    usuario = _usuario()
    if usuario is None:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401
    db = None
    try:
        datos = request.get_json()
        if not isinstance(datos, dict) or datos.get('tipo') not in ('aporte', 'retiro'):
            raise ValueError('Selecciona aporte o retiro')
        monto = dinero(datos.get('monto'))
        if monto <= 0:
            raise ValueError('El importe debe ser mayor que cero')
        nota = datos.get('nota', '')
        if not isinstance(nota, str) or len(nota.strip()) > 255:
            raise ValueError('La nota admite hasta 255 caracteres')
        nota = nota.strip()
        referencia = _referencia(datos.get('referencia'))
        db = _conexion()
        with db.conn.cursor(dictionary=True) as cursor:
            _meta(cursor, meta_id, usuario, bloquear=True)
            cursor.execute('SELECT * FROM meta_ahorro_movimiento WHERE referencia=%s', (referencia,))
            anterior = cursor.fetchone()
            if anterior:
                if (anterior['id_meta'], anterior['tipo'], anterior['monto'], anterior['nota']) != (meta_id, datos['tipo'], monto, nota):
                    raise ValueError('La referencia ya corresponde a otra operación')
                return jsonify({'id': anterior['id'], 'message': 'Movimiento ya registrado'}), 200
            cursor.execute("SELECT COALESCE(SUM(CASE WHEN tipo='aporte' THEN monto ELSE -monto END),0) AS saldo "
                           "FROM meta_ahorro_movimiento WHERE id_meta=%s", (meta_id,))
            saldo = cursor.fetchone()['saldo']
            if datos['tipo'] == 'retiro' and monto > saldo:
                raise ValueError('El retiro no puede superar el ahorro registrado')
            if datos['tipo'] == 'aporte' and saldo + monto > Decimal('9999999999999.99'):
                raise ValueError('El saldo supera el límite permitido')
            cursor.execute('INSERT INTO meta_ahorro_movimiento (id_meta,tipo,monto,nota,referencia) VALUES (%s,%s,%s,%s,%s)',
                           (meta_id, datos['tipo'], monto, nota, referencia))
            db.conn.commit()
            return jsonify({'id': cursor.lastrowid, 'message': 'Movimiento registrado'}), 201
    except Exception as exc:
        if db and db.conn:
            db.conn.rollback()
        return _error(exc)
    finally:
        if db:
            db.close()

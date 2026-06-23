"""Rutas API de Transacciones conectadas a base de datos MySQL."""

import logging
import os
import tempfile
import io
import datetime
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector
from src.business.services.etl_cuenta_bancaria import ETLCuentaBancaria, validate_bank_excel_file
from src.business.services.etl_tarjeta_credito import ETLTarjetaCredito, validate_excel_file

try:
    import pandas as pd
except ImportError:
    pd = None

bp = Blueprint('transacciones', __name__, url_prefix='/api/transacciones')

logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _resolve_tipo_id(db: DatabaseConnector, nombre_tipo: str):
    if not nombre_tipo:
        nombre_tipo = 'gasto'
    rows = db.execute_query(
        "SELECT id_tipo FROM tipo_movimiento WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
        (nombre_tipo,),
    )
    if rows:
        return rows[0]['id_tipo']
    return db.execute_non_query("INSERT INTO tipo_movimiento (nombre) VALUES (%s)", (nombre_tipo,))


def _resolve_categoria_id(db: DatabaseConnector, nombre_categoria: str):
    if not nombre_categoria:
        return None
    rows = db.execute_query(
        "SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
        (nombre_categoria,),
    )
    if rows:
        return rows[0]['id_categoria']
    return db.execute_non_query("INSERT INTO categoria (nombre) VALUES (%s)", (nombre_categoria,))


def _default_cuenta_id(db: DatabaseConnector, user_id: int):
    rows = db.execute_query(
        """
        SELECT id_cuenta
        FROM cuenta
        WHERE id_persona = %s
          AND COALESCE(LOWER(estado), 'activo') IN ('activo', 'activa')
        ORDER BY id_cuenta ASC
        LIMIT 1
        """,
        (user_id,),
    )
    if rows:
        return rows[0]['id_cuenta']
    return None


def _user_accounts(db: DatabaseConnector, user_id: int):
    rows = db.execute_query(
        """
        SELECT id_cuenta, nombre
        FROM cuenta
        WHERE id_persona = %s
          AND COALESCE(LOWER(estado), 'activo') IN ('activo', 'activa')
        ORDER BY id_cuenta
        """,
        (user_id,),
    )
    return rows or []


def _user_cards(db: DatabaseConnector, user_id: int):
    rows = db.execute_query(
        """
        SELECT tc.id_tarjeta,
               tc.numero_tarjeta,
               CONCAT(COALESCE(tc.banco, 'Tarjeta'), ' ****', RIGHT(tc.numero_tarjeta, 4)) AS nombre
        FROM tarjeta_credito tc
        LEFT JOIN estado_tarjeta et ON tc.id_estado = et.id_estado
        WHERE tc.id_persona = %s
          AND COALESCE(LOWER(et.nombre), 'activa') = 'activa'
        ORDER BY tc.fecha_creacion DESC, tc.id_tarjeta DESC
        """,
        (user_id,),
    )
    return rows or []


@bp.route('/debug/status', methods=['GET'])
def debug_status():
    """Endpoint simple que NO requiere JWT para verificar el estado de la sesión."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    return jsonify({
        'timestamp': str(datetime.datetime.now()),
        'server_status': 'ok',
        'has_token': bool(token),
        'token_length': len(token) if token else 0,
        'instructions': {
            'paso_1': 'Abre F12 → Console',
            'paso_2': 'Verifica que localStorage tenga token:',
            'comando_check': "console.log(localStorage.getItem('token'))",
            'paso_3': 'Si NO ves un token long (tipo: eyJ...), debes hacer LOGIN de nuevo',
            'paso_4': 'Si ves un token, prueba:',
            'comando_whoami': "fetch('/api/transacciones/debug/whoami', {headers:{'Authorization':'Bearer ' + localStorage.getItem('token')}}).then(r=>r.json()).then(d => console.log(JSON.stringify(d, null, 2)))"
        }
    }), 200


@bp.route('/debug/whoami', methods=['GET'])
def debug_whoami():
    """Para debugging: retorna el ID del usuario actual y sus tarjetas/cuentas.
    
    Llama desde la consola del navegador así:
    fetch('/api/transacciones/debug/whoami', {
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}
    }).then(r => r.json()).then(console.log)
    """
    db = DatabaseConnector()
    try:
        verify_jwt_in_request()
        user_id = _get_user_id()
        tarjetas = db.execute_query(
            "SELECT id_tarjeta, banco, numero_tarjeta FROM tarjeta_credito WHERE id_persona = %s",
            (user_id,)
        )
        cuentas = db.execute_query(
                        """
                        SELECT id_cuenta, nombre
                        FROM cuenta
                        WHERE id_persona = %s
                            AND COALESCE(LOWER(estado), 'activo') IN ('activo', 'activa')
                        ORDER BY id_cuenta
                        """,
                        (user_id,),
        )
        return jsonify({
            'id_persona': user_id,
            'tarjetas': tarjetas or [],
            'cuentas': cuentas or [],
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'msg': 'Llama desde la CONSOLA del navegador (F12 → Console) con este comando:',
            'comando': "fetch('/api/transacciones/debug/whoami', {headers:{'Authorization':'Bearer ' + localStorage.getItem('token')}}).then(r=>r.json()).then(console.log)"
        }), 401
    finally:
        db.close()


@bp.route('/import/catalogos', methods=['GET'])
def import_catalogos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        cuentas = _user_accounts(db, user_id)
        tarjetas = _user_cards(db, user_id)
        return jsonify({'cuentas': cuentas or [], 'tarjetas': tarjetas}), 200
    except Exception as e:
        logger.error("Error cargando catalogos de importacion: %s", e)
        return jsonify({'message': 'Error al cargar catalogos de importacion'}), 500
    finally:
        db.close()


@bp.route('/import/upload', methods=['POST'])
def import_upload():
    verify_jwt_in_request()
    db = DatabaseConnector()
    tmp_path = None
    try:
        user_id = _get_user_id()
        source = (request.form.get('source') or '').strip().lower()
        file = request.files.get('file')

        logger.warning("UPLOAD DEBUG - source='%s' file='%s' form=%s", source, file and file.filename, dict(request.form))

        if source not in ('cuenta_bancaria', 'tarjeta_credito'):
            logger.warning("UPLOAD 400 - source invalido: '%s'", source)
            return jsonify({'message': 'Origen de importacion invalido'}), 400
        if not file or not file.filename:
            logger.warning("UPLOAD 400 - sin archivo")
            return jsonify({'message': 'Debes seleccionar un archivo Excel'}), 400

        suffix = Path(file.filename).suffix.lower()
        if suffix not in ('.xlsx', '.xls'):
            logger.warning("UPLOAD 400 - extension invalida: '%s'", suffix)
            return jsonify({'message': 'Formato no soportado. Usa .xlsx o .xls'}), 400

        # mkstemp cierra el fd antes de guardar para evitar conflicto en Windows
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        file.save(tmp_path)

        if source == 'cuenta_bancaria':
            id_cuenta = request.form.get('id_cuenta', type=int)
            if not id_cuenta:
                available_cuentas = db.execute_query(
                    """
                    SELECT COUNT(*) as total
                    FROM cuenta
                    WHERE id_persona = %s
                      AND COALESCE(LOWER(estado), 'activo') IN ('activo', 'activa')
                    """,
                    (user_id,)
                )
                total_cuentas = available_cuentas[0]['total'] if available_cuentas else 0
                error_msg = f'No hay cuentas bancarias activas registradas para tu usuario (ID: {user_id}). Activa o crea una cuenta primero.'
                if total_cuentas > 0:
                    error_msg = 'Debes seleccionar una cuenta bancaria'
                return jsonify({'message': error_msg}), 400

            cuenta = db.execute_query(
                """
                SELECT id_cuenta
                FROM cuenta
                WHERE id_cuenta = %s
                  AND id_persona = %s
                  AND COALESCE(LOWER(estado), 'activo') IN ('activo', 'activa')
                LIMIT 1
                """,
                (id_cuenta, user_id),
            )
            if not cuenta:
                return jsonify({'message': 'Cuenta no encontrada, no pertenece al usuario o esta inactiva'}), 403

            valid, errors = validate_bank_excel_file(tmp_path)
            if not valid:
                return jsonify({'message': 'Archivo invalido', 'errors': errors}), 400

            etl = ETLCuentaBancaria(db)
            processed, row_errors = etl.process_file(tmp_path, user_id, id_cuenta)
        else:
            id_tarjeta = request.form.get('id_tarjeta', type=int)
            logger.warning("UPLOAD DEBUG - id_tarjeta raw='%s' parsed=%s", request.form.get('id_tarjeta'), id_tarjeta)
            if not id_tarjeta:
                available_cards = db.execute_query(
                    """
                    SELECT COUNT(*) as total
                    FROM tarjeta_credito tc
                    LEFT JOIN estado_tarjeta et ON tc.id_estado = et.id_estado
                    WHERE tc.id_persona = %s
                      AND COALESCE(LOWER(et.nombre), 'activa') = 'activa'
                    """,
                    (user_id,)
                )
                total_cards = available_cards[0]['total'] if available_cards else 0
                error_msg = f'No hay tarjetas activas registradas para tu usuario (ID: {user_id}). Activa o crea una tarjeta primero.'
                if total_cards > 0:
                    error_msg = 'Debes seleccionar una tarjeta de credito'
                logger.warning("UPLOAD 400 - id_tarjeta vacio o invalido")
                return jsonify({'message': error_msg}), 400

            tarjeta = db.execute_query(
                """
                SELECT tc.id_tarjeta
                FROM tarjeta_credito tc
                LEFT JOIN estado_tarjeta et ON tc.id_estado = et.id_estado
                WHERE tc.id_tarjeta = %s
                  AND tc.id_persona = %s
                  AND COALESCE(LOWER(et.nombre), 'activa') = 'activa'
                LIMIT 1
                """,
                (id_tarjeta, user_id),
            )
            if not tarjeta:
                return jsonify({'message': 'Tarjeta no encontrada, no pertenece al usuario o esta inactiva'}), 403

            valid, errors = validate_excel_file(tmp_path)
            if not valid:
                logger.warning("UPLOAD 400 - archivo invalido: %s", errors)
                return jsonify({'message': 'Archivo invalido', 'errors': errors}), 400

            etl = ETLTarjetaCredito(db)
            processed, row_errors = etl.process_file(tmp_path, user_id, id_tarjeta)

        return jsonify(
            {
                'message': 'Importacion completada',
                'processed': processed,
                'errors': row_errors,
            }
        ), 200
    except Exception as e:
        logger.exception("Error en importacion ETL de transacciones: %s", e)
        return jsonify({'message': 'Error al procesar importacion ETL'}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        db.close()



@bp.route('/import/upload-folder', methods=['POST'])
def import_upload_folder():
    """Procesa todos los archivos Excel de una carpeta en orden cronologico."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        data = request.get_json(silent=True) or {}
        folder_path = (data.get('folder_path') or '').strip()
        id_tarjeta = data.get('id_tarjeta')

        if not folder_path:
            return jsonify({'message': 'Debes indicar la ruta de la carpeta (folder_path)'}), 400
        if not id_tarjeta:
            return jsonify({'message': 'Debes indicar id_tarjeta'}), 400

        tarjeta = db.execute_query(
                        """
                        SELECT tc.id_tarjeta
                        FROM tarjeta_credito tc
                        LEFT JOIN estado_tarjeta et ON tc.id_estado = et.id_estado
                        WHERE tc.id_tarjeta = %s
                            AND tc.id_persona = %s
                            AND COALESCE(LOWER(et.nombre), 'activa') = 'activa'
                        LIMIT 1
                        """,
            (id_tarjeta, user_id)
        )
        if not tarjeta:
                        return jsonify({'message': 'Tarjeta no encontrada, no pertenece al usuario o esta inactiva'}), 403

        etl = ETLTarjetaCredito(db)
        resumen = etl.process_folder(folder_path, user_id, id_tarjeta)

        if 'error' in resumen:
            return jsonify({'message': resumen['error']}), 400

        return jsonify({
            'message': 'Carga masiva completada',
            'total_archivos': resumen['total_archivos'],
            'total_insertados': resumen['total_insertados'],
            'total_errores': resumen['total_errores'],
            'detalle': resumen['detalle'],
        }), 200
    except Exception as e:
        logger.exception('Error en carga masiva de carpeta: %s', e)
        return jsonify({'message': 'Error en carga masiva', 'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/import/template', methods=['GET'])
def import_template():
    verify_jwt_in_request()
    source = (request.args.get('source') or '').strip().lower()
    if source not in ('cuenta_bancaria', 'tarjeta_credito'):
        return jsonify({'message': 'Origen de plantilla invalido'}), 400
    if pd is None:
        return jsonify({'message': 'pandas no disponible para generar plantilla'}), 500

    if source == 'cuenta_bancaria':
        rows = [
            {
                'FECHA': '01/01/2026',
                'DESCRIPCION SUCURSAL': 'ABONO INTERES',
                'DCTO.': 'ABONO',
                'VALOR': 1.36,
                'SALDO': 996967.62,
            },
            {
                'FECHA': '02/01/2026',
                'DESCRIPCION SUCURSAL': 'COMPRA SUPERMERCADO',
                'DCTO.': 'CARGO',
                'VALOR': -125.50,
                'SALDO': 996842.12,
            },
        ]
        filename = 'plantilla_etl_cuenta_bancaria.xlsx'
    else:
        rows = [
            {
                'Fecha': '2026-01-10',
                'Concepto': 'Compra combustible',
                'Monto': 50.25,
                'Cuotas': 1,
                'Categoria': 'Transporte',
                'Referencia': 'REF-001',
            },
            {
                'Fecha': '2026-01-11',
                'Concepto': 'Supermercado',
                'Monto': 120.0,
                'Cuotas': 2,
                'Categoria': 'Compras',
                'Referencia': 'REF-002',
            },
        ]
        filename = 'plantilla_etl_tarjeta_credito.xlsx'

    output = io.BytesIO()
    pd.DataFrame(rows).to_excel(output, index=False, sheet_name='Plantilla')
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@bp.route('', methods=['GET'])
def list_transacciones():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        limit = min(int(request.args.get('limit', 100)), 500)
        rows = db.execute_query(
            """
            SELECT
                m.id_movimiento,
                DATE(m.fecha_creacion) AS fecha,
                COALESCE(m.nota, m.codigo, 'Sin descripción') AS descripcion,
                COALESCE(ca.nombre, 'General') AS categoria,
                COALESCE(tm.nombre, 'gasto') AS tipo,
                m.monto
            FROM movimiento m
            INNER JOIN cuenta cu ON m.id_cuenta = cu.id_cuenta
            LEFT JOIN categoria ca ON m.id_categoria = ca.id_categoria
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE cu.id_persona = %s
            ORDER BY m.fecha_creacion DESC, m.id_movimiento DESC
            LIMIT %s
            """,
            (user_id, limit),
        )

        result = []
        for row in rows:
            monto = float(row.get('monto') or 0)
            tipo = (row.get('tipo') or '').lower()
            signed_monto = monto if tipo == 'ingreso' else -abs(monto)
            result.append({
                'id': row['id_movimiento'],
                'fecha': row['fecha'].isoformat() if row.get('fecha') else None,
                'descripcion': row.get('descripcion') or 'Sin descripción',
                'categoria': row.get('categoria') or 'General',
                'monto': signed_monto,
                'tipo': tipo,
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error("Error listando transacciones: %s", e)
        return jsonify({'message': 'Error al listar transacciones'}), 500
    finally:
        db.close()


@bp.route('', methods=['POST'])
def create_transaccion():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        descripcion = payload.get('descripcion') or payload.get('nota') or 'Sin descripción'
        categoria = payload.get('categoria')
        tipo = (payload.get('tipo') or ('ingreso' if float(payload.get('monto', 0) or 0) >= 0 else 'gasto')).lower()
        monto = abs(float(payload.get('monto', 0) or 0))
        fecha = payload.get('fecha')
        id_estado = int(payload.get('id_estado', 2))

        id_tipo = payload.get('id_tipo') or _resolve_tipo_id(db, tipo)
        id_categoria = payload.get('id_categoria') or _resolve_categoria_id(db, categoria)
        id_cuenta = payload.get('id_cuenta') or _default_cuenta_id(db, user_id)
        if not id_cuenta:
            return jsonify({'message': 'No existe una cuenta para registrar la transacción'}), 400

        mov_id = db.execute_non_query(
            """
            INSERT INTO movimiento (
                codigo, monto, id_tipo, id_estado, id_categoria, id_beneficiario,
                fecha_creacion, id_cuenta, nota, numero_transaccion
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                COALESCE(%s, NOW()), %s, %s, %s
            )
            """,
            (
                payload.get('codigo') or f"MOV-{user_id}-{id_cuenta}",
                monto,
                id_tipo,
                id_estado,
                id_categoria,
                payload.get('id_beneficiario'),
                fecha,
                id_cuenta,
                descripcion,
                payload.get('numero_transaccion'),
            ),
        )

        if not mov_id:
            return jsonify({'message': 'No se pudo crear la transacción'}), 500

        created = db.execute_query(
            """
            SELECT
                m.id_movimiento,
                DATE(m.fecha_creacion) AS fecha,
                COALESCE(m.nota, m.codigo, 'Sin descripción') AS descripcion,
                COALESCE(ca.nombre, 'General') AS categoria,
                COALESCE(tm.nombre, 'gasto') AS tipo,
                m.monto
            FROM movimiento m
            LEFT JOIN categoria ca ON m.id_categoria = ca.id_categoria
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE m.id_movimiento = %s
            LIMIT 1
            """,
            (mov_id,),
        )

        if not created:
            return jsonify({'message': 'Transacción creada'}), 201

        row = created[0]
        valor = float(row.get('monto') or 0)
        tipo_row = (row.get('tipo') or '').lower()
        return jsonify({
            'id': row['id_movimiento'],
            'fecha': row['fecha'].isoformat() if row.get('fecha') else None,
            'descripcion': row.get('descripcion') or 'Sin descripción',
            'categoria': row.get('categoria') or 'General',
            'monto': valor if tipo_row == 'ingreso' else -abs(valor),
            'tipo': tipo_row,
        }), 201
    except Exception as e:
        logger.error("Error creando transacción: %s", e)
        return jsonify({'message': 'Error al crear transacción'}), 500
    finally:
        db.close()


@bp.route('/<int:transaccion_id>', methods=['PUT'])
def update_transaccion(transaccion_id):
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        exists = db.execute_query(
            """
            SELECT m.id_movimiento
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            WHERE m.id_movimiento = %s AND c.id_persona = %s
            LIMIT 1
            """,
            (transaccion_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Transacción no encontrada'}), 404

        categoria_id = payload.get('id_categoria')
        if payload.get('categoria'):
            categoria_id = _resolve_categoria_id(db, payload.get('categoria'))

        tipo_id = payload.get('id_tipo')
        if payload.get('tipo'):
            tipo_id = _resolve_tipo_id(db, payload.get('tipo'))

        monto = payload.get('monto')
        monto = abs(float(monto)) if monto is not None else None

        db.execute_non_query(
            """
            UPDATE movimiento
            SET nota = COALESCE(%s, nota),
                monto = COALESCE(%s, monto),
                fecha_creacion = COALESCE(%s, fecha_creacion),
                id_categoria = COALESCE(%s, id_categoria),
                id_tipo = COALESCE(%s, id_tipo),
                id_estado = COALESCE(%s, id_estado)
            WHERE id_movimiento = %s
            """,
            (
                payload.get('descripcion'),
                monto,
                payload.get('fecha'),
                categoria_id,
                tipo_id,
                payload.get('id_estado'),
                transaccion_id,
            ),
        )

        return jsonify({'message': 'Transacción actualizada'}), 200
    except Exception as e:
        logger.error("Error actualizando transacción %s: %s", transaccion_id, e)
        return jsonify({'message': 'Error al actualizar transacción'}), 500
    finally:
        db.close()


@bp.route('/<int:transaccion_id>', methods=['DELETE'])
def delete_transaccion(transaccion_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        exists = db.execute_query(
            """
            SELECT m.id_movimiento
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            WHERE m.id_movimiento = %s AND c.id_persona = %s
            LIMIT 1
            """,
            (transaccion_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Transacción no encontrada'}), 404

        db.execute_non_query("DELETE FROM movimiento WHERE id_movimiento = %s", (transaccion_id,))
        return jsonify({'message': 'Transacción eliminada'}), 200
    except Exception as e:
        logger.error("Error eliminando transacción %s: %s", transaccion_id, e)
        return jsonify({'message': 'Error al eliminar transacción'}), 500
    finally:
        db.close()

"""Inserta el endpoint /import/upload-folder en transacciones.py"""
path = 'src/routes/transacciones.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

new_endpoint = """
@bp.route('/import/upload-folder', methods=['POST'])
def import_upload_folder():
    \"\"\"Procesa todos los archivos Excel de una carpeta en orden cronologico.\"\"\"
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
            'SELECT id_tarjeta FROM tarjeta_credito WHERE id_tarjeta = %s AND id_persona = %s',
            (id_tarjeta, user_id)
        )
        if not tarjeta:
            return jsonify({'message': 'Tarjeta no encontrada o no pertenece al usuario'}), 403

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


"""

marker = "@bp.route('/import/template', methods=['GET'])"
if marker not in content:
    print("ERROR: marcador no encontrado")
else:
    content = content.replace(marker, new_endpoint + marker)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK - endpoint agregado")

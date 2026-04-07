from src.database.db_connector import DatabaseConnector

try:
    print("=== Iniciando debug ===")
    
    # Prueba conexión directa
    db = DatabaseConnector()
    print(f"1. Conexión establecida: {db.conn is not None}")
    
    if db.conn:
        cursor = db.conn.cursor(dictionary=True)
        
        # Prueba SELECT directo
        print("2. Ejecutando SELECT directo...")
        cursor.execute("SELECT id_persona, nombre, apellido, correo_electronico FROM persona WHERE estado = 1 ORDER BY id_persona DESC LIMIT 1")
        row = cursor.fetchone()
        print(f"   Resultado: {row}")
        
        cursor.close()
        db.conn.close()

    # Ahora prueba la función
    print("\n3. Probando load_active_user_data()...")
    from src.views.sidebar import load_active_user_data
    datos = load_active_user_data()
    print(f"   Nombre: {datos['name']}")
    print(f"   Email: {datos['email']}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

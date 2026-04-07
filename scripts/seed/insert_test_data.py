"""
Script para insert datos de prueba en tabla constantes
Conexión directa a BD sin usar MySQL CLI
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.db_connector import DatabaseConnector

def insert_test_data():
    """Inserta datos de prueba en la tabla constantes"""
    db = DatabaseConnector()
    conn = db.conn
    
    if not conn:
        print("❌ Error: No se pudo conectar a la BD")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        create_table = """
        CREATE TABLE IF NOT EXISTS constantes (
            id_constante INT AUTO_INCREMENT PRIMARY KEY,
            categoria VARCHAR(50) NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            valor TEXT NOT NULL,
            tipo_dato ENUM('STRING','INTEGER','DECIMAL','BOOLEAN','JSON','DATE') NOT NULL,
            descripcion TEXT,
            es_editable TINYINT(1) DEFAULT 1,
            estado TINYINT(1) DEFAULT 1,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_nombre (nombre),
            INDEX idx_categoria (categoria),
            INDEX idx_estado (estado)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        cursor.execute(create_table)
        conn.commit()
        print("✅ Tabla constantes creada/verificada")
        
        # Limpiar datos anteriores
        cursor.execute("DELETE FROM constantes")
        conn.commit()
        
        # Datos de prueba
        test_data = [
            # FINANCIERO
            ('FINANCIERO', 'IVA', '0.19', 'DECIMAL', 'Impuesto al valor agregado - 19%', 0, 1),
            ('FINANCIERO', 'TASA_INTERES_AHORRO', '0.04', 'DECIMAL', 'Rendimiento anual para cuentas de ahorro', 1, 1),
            ('FINANCIERO', 'TASA_INTERES_PLAZO', '0.05', 'DECIMAL', 'Rendimiento anual para depósitos a plazo', 1, 1),
            ('FINANCIERO', 'TASA_COMISION_TRANSFERENCIA', '0.001', 'DECIMAL', 'Comisión por transferencia bancaria', 1, 1),
            
            # GENERAL
            ('GENERAL', 'MONEDA_PRINCIPAL', 'COP', 'STRING', 'Moneda principal de la aplicación', 0, 1),
            ('GENERAL', 'PAIS', 'Colombia', 'STRING', 'País de operación', 0, 1),
            ('GENERAL', 'IDIOMA_DEFECTO', 'es', 'STRING', 'Código de idioma por defecto', 1, 1),
            ('GENERAL', 'TEMA_MODO_OSCURO', 'false', 'BOOLEAN', 'Activar modo oscuro por defecto', 1, 1),
            
            # LIMITES
            ('LIMITES', 'MAX_TARJETA_CREDITO', '10000000', 'INTEGER', 'Límite máximo de línea de crédito', 1, 1),
            ('LIMITES', 'MIN_DEPOSITO', '50000', 'INTEGER', 'Depósito mínimo permitido', 1, 1),
            ('LIMITES', 'MAX_TRANSFERENCIA_DIARIA', '50000000', 'INTEGER', 'Límite máximo de transferencia por día', 1, 1),
            
            # NOTIFICACIONES
            ('NOTIFICACIONES', 'NOTIFICACIONES_HABILITADAS', 'true', 'BOOLEAN', 'Enviar notificaciones a usuarios', 1, 1),
            ('NOTIFICACIONES', 'EMAIL_NOTIFICACIONES', 'app@empresa.com', 'STRING', 'Email para enviar notificaciones', 1, 1),
            
            # SISTEMA
            ('SISTEMA', 'VERSION_APP', '1.0.0', 'STRING', 'Versión actual de la aplicación', 0, 1),
            ('SISTEMA', 'MODO_MANTENIMIENTO', 'false', 'BOOLEAN', 'Activar modo de mantenimiento', 1, 1),
            ('SISTEMA', 'CONFIG_BACKUP', '{"frecuencia": "diaria", "hora": "02:00"}', 'JSON', 'Configuración de copias de seguridad', 1, 1),
            ('SISTEMA', 'FECHA_ULTIMO_BACKUP', '2026-04-07', 'DATE', 'Fecha del último backup realizado', 1, 1),
        ]
        
        # Insertar datos
        insert_sql = """
        INSERT INTO constantes 
        (categoria, nombre, valor, tipo_dato, descripcion, es_editable, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_sql, test_data)
        conn.commit()
        
        print(f"✅ {cursor.rowcount} constantes insertadas")
        
        # Verificar
        cursor.execute("SELECT COUNT(*) as total FROM constantes WHERE estado = 1")
        result = cursor.fetchone()
        total = result[0] if result else 0
        print(f"✅ Total de constantes activas: {total}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    insert_test_data()

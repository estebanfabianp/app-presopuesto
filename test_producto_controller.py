"""
Script de prueba para el controlador de productos.
Permite verificar que las funciones funcionen correctamente.
"""

import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from business.services.producto_controller import (
    obtener_productos_por_usuario,
    obtener_resumen_productos_por_usuario
)

def test_productos_usuario():
    """
    Prueba las funciones de productos del controlador.
    """
    print("=" * 60)
    print("PRUEBA DEL CONTROLADOR DE PRODUCTOS")
    print("=" * 60)
    
    user_id = 1  # ID del usuario de prueba
    
    print(f"\n1. Probando obtener_productos_por_usuario(user_id={user_id})...")
    try:
        productos = obtener_productos_por_usuario(user_id)
        print(f"✅ Productos obtenidos: {len(productos)}")
        
        if productos:
            print("\n📊 Primeros productos encontrados:")
            for i, producto in enumerate(productos[:3], 1):
                print(f"  {i}. {producto['nombre']} ({producto['tipo_display']})")
                print(f"     Saldo: ${producto['saldo_actual']:,.2f}")
                print(f"     Valor efectivo: ${producto['valor_efectivo']:,.2f}")
                print()
        else:
            print("ℹ️  No se encontraron productos para este usuario.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    print(f"\n2. Probando obtener_resumen_productos_por_usuario(user_id={user_id})...")
    try:
        resumen = obtener_resumen_productos_por_usuario(user_id)
        print("✅ Resumen obtenido exitosamente")
        
        print("\n📈 RESUMEN POR TIPO DE PRODUCTO:")
        print("-" * 50)
        
        for tipo, datos in resumen.items():
            if tipo != 'total_patrimonio':
                print(f"{tipo.replace('_', ' ').title()}:")
                print(f"  • Cantidad: {datos.get('cantidad', 0)} productos")
                print(f"  • Total: ${datos.get('total', 0):,.2f}")
                print()
        
        print(f"💰 PATRIMONIO TOTAL: ${resumen.get('total_patrimonio', 0):,.2f}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    return True

def test_conexion_bd():
    """
    Prueba básica de conexión a la base de datos.
    """
    print("\n3. Probando conexión a base de datos...")
    try:
        from database.db_connector import DatabaseConnector
        
        db = DatabaseConnector()
        if db.is_connected():
            print("✅ Conexión a BD exitosa")
            
            # Prueba simple de query
            resultado = db.execute_query("SELECT COUNT(*) as total FROM persona")
            if resultado:
                print(f"✅ Query de prueba exitosa. Personas en BD: {resultado[0]['total']}")
            return True
        else:
            print("❌ No se pudo conectar a la base de datos")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DEL CONTROLADOR DE PRODUCTOS")
    print()
    
    # Probar conexión primero
    conexion_ok = test_conexion_bd()
    
    if conexion_ok:
        # Probar funciones de productos
        productos_ok = test_productos_usuario()
        
        print("\n" + "=" * 60)
        if productos_ok:
            print("🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
            print("✅ El controlador de productos está funcionando correctamente")
        else:
            print("⚠️  ALGUNAS PRUEBAS FALLARON")
            print("🔧 Revisar la configuración de la base de datos y las consultas")
    else:
        print("\n" + "=" * 60)
        print("❌ NO SE PUEDE CONTINUAR SIN CONEXIÓN A LA BASE DE DATOS")
        print("🔧 Verificar configuración de MySQL y credenciales")
    
    print("=" * 60)
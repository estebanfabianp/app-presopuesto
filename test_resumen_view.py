"""
Script de prueba para la vista de resumen con datos reales.
Permite verificar que la integración funcione correctamente.
"""

import sys
import os
import flet as ft

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_resumen_view():
    """
    Prueba la vista de resumen con datos reales.
    """
    print("🧪 PROBANDO LA VISTA DE RESUMEN CON DATOS REALES")
    print("=" * 60)
    
    def main(page: ft.Page):
        page.title = "Test - Resumen Financiero"
        page.window.width = 1200
        page.window.height = 800
        
        try:
            # Importar la vista de resumen
            from views.resumen import ResumenView
            
            # Crear instancia de la vista con user_id = 1
            resumen_view = ResumenView(page, user_id=1)
            
            print("✅ Vista de resumen creada exitosamente")
            print(f"📊 Productos cargados: {len(resumen_view.productos_usuario)}")
            
            # Mostrar información de los productos cargados
            if resumen_view.productos_usuario:
                print("\n📈 PRODUCTOS ENCONTRADOS:")
                for i, producto in enumerate(resumen_view.productos_usuario, 1):
                    print(f"  {i}. {producto['nombre']} ({producto['tipo_display']})")
                    print(f"     Saldo: ${producto['saldo_actual']:,.2f}")
                    print(f"     Disponible: ${producto['saldo_disponible']:,.2f}")
            
            # Mostrar resumen por categorías
            resumen = resumen_view.resumen_productos
            print("\n💰 RESUMEN FINANCIERO:")
            print(f"  • Cuentas bancarias: {resumen['cuentas_bancarias']['cantidad']} productos, ${resumen['cuentas_bancarias']['total']:,.2f}")
            print(f"  • Tarjetas de crédito: {resumen['tarjetas_credito']['cantidad']} productos, ${resumen['tarjetas_credito']['total']:,.2f}")
            print(f"  • Préstamos: {resumen['prestamos']['cantidad']} productos, ${resumen['prestamos']['total']:,.2f}")
            print(f"  • Fondos inversión: {resumen['fondos_inversion']['cantidad']} productos, ${resumen['fondos_inversion']['total']:,.2f}")
            print(f"  • PATRIMONIO TOTAL: ${resumen['total_patrimonio']:,.2f}")
            
            # Construir y mostrar la UI
            print("\n🎨 Construyendo interfaz...")
            ui = resumen_view.build()
            page.add(ui)
            print("✅ Interfaz construida y mostrada exitosamente")
            
        except Exception as e:
            print(f"❌ Error al crear la vista: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Crear una vista de error simple
            page.add(
                ft.Column([
                    ft.Text("Error al cargar la vista de resumen", size=20, color="red"),
                    ft.Text(str(e), size=14),
                    ft.ElevatedButton("Cerrar", on_click=lambda e: page.window.close())
                ])
            )

    print("\n🚀 Iniciando aplicación Flet...")
    print("   (Se abrirá una ventana con la vista de resumen)")
    print("   Cierra la ventana cuando hayas terminado de revisar")
    
    # Ejecutar la app Flet
    ft.app(target=main)
    
    print("\n✅ Prueba completada")

if __name__ == "__main__":
    test_resumen_view()
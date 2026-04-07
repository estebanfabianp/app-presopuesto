"""
Controlador para operaciones relacionadas con productos.
Incluye funciones para listar, obtener, crear, actualizar y eliminar productos.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from database.db_connector import DatabaseConnector
from typing import List, Dict, Any, Optional

def listar():
    """
    Lista todos los productos.

    Returns:
        list: Lista de productos (actualmente vacío).
    """
    return []

def obtener(id):
    """
    Obtiene un producto por su ID.

    Args:
        id (int): Identificador del producto.

    Returns:
        None: No implementado, retorna None.
    """
    return None

def crear(data):
    """
    Crea un nuevo producto.

    Args:
        data (dict): Datos del producto a crear.

    Returns:
        dict: Datos del producto creado (actualmente vacío).
    """
    return {}

def actualizar(id, data):
    """
    Actualiza un producto existente.

    Args:
        id (int): Identificador del producto.
        data (dict): Datos actualizados del producto.

    Returns:
        dict: Datos del producto actualizado (actualmente vacío).
    """
    return {}

def eliminar(id):
    """
    Elimina un producto por su ID.

    Args:
        id (int): Identificador del producto.

    Returns:
        dict: Resultado de la eliminación (actualmente vacío).
    """
    return {}

def obtener_productos_por_usuario(user_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene todos los productos financieros de un usuario con sus saldos.
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        List[Dict[str, Any]]: Lista de productos con sus saldos
    """
    try:
        db_connector = DatabaseConnector()

        # Estrategia principal: usar vista unificada de productos si existe
        query_view = """
        SELECT
            id_producto,
            tipo_producto,
            nombre,
            saldo_actual,
            saldo_disponible,
            limite_credito,
            tasa_interes,
            fecha_apertura,
            estado,
            tipo_display,
            valor_efectivo
        FROM v_producto_unificado
        WHERE id_persona = %s
        ORDER BY tipo_producto, nombre
        """

        resultados = db_connector.execute_query(query_view, (user_id,))
        
        # Fallback: consulta simplificada si la vista no existe o retorna vacío
        if not resultados:
            query = """
            SELECT 
                c.id_cuenta as id_producto,
                'cuenta_bancaria' as tipo_producto,
                c.nombre as nombre,
                c.saldo_inicial as saldo_actual,
                c.saldo_inicial as saldo_disponible,
                0 as limite_credito,
                0 as tasa_interes,
                c.fecha_creacion as fecha_apertura,
                'ACTIVO' as estado,
                'Cuenta Bancaria' as tipo_display,
                c.saldo_inicial as valor_efectivo
            FROM cuenta c
            WHERE c.id_persona = %s
            ORDER BY c.nombre
            """

            resultados = db_connector.execute_query(query, (user_id,))
        
        if not resultados:
            return []
            
        productos = []
        for row in resultados:
            tipo_mapeado = row['tipo_producto']

            if tipo_mapeado in ('CUENTA', 'TARJETA', 'PRESTAMO', 'ACTIVO'):
                tipo_mapeado = {
                    'CUENTA': 'cuenta_bancaria',
                    'TARJETA': 'tarjeta_credito',
                    'PRESTAMO': 'prestamo',
                    'ACTIVO': 'fondo_inversion'
                }.get(tipo_mapeado, 'otro')
            
            producto = {
                'id_producto': row['id_producto'],
                'tipo_producto': tipo_mapeado,
                'nombre': row['nombre'],
                'saldo_actual': float(row['saldo_actual']) if row['saldo_actual'] else 0.0,
                'saldo_disponible': float(row['saldo_disponible']) if row['saldo_disponible'] else 0.0,
                'limite_credito': float(row['limite_credito']) if row['limite_credito'] else 0.0,
                'tasa_interes': float(row['tasa_interes']) if row['tasa_interes'] else 0.0,
                'fecha_apertura': row['fecha_apertura'],
                'estado': row['estado'],
                'tipo_display': row['tipo_display'],
                'valor_efectivo': float(row['valor_efectivo']) if row['valor_efectivo'] else 0.0
            }
            productos.append(producto)
            
        return productos
        
    except Exception as e:
        print(f"Error al obtener productos del usuario {user_id}: {str(e)}")
        return []
        
def obtener_resumen_productos_por_usuario(user_id: int) -> Dict[str, Any]:
    """
    Obtiene un resumen agrupado de productos por tipo para el dashboard.
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        Dict[str, Any]: Resumen agrupado por tipo de producto
    """
    try:
        productos = obtener_productos_por_usuario(user_id)
        
        if not productos:
            return {
                'cuentas_bancarias': {'total': 0, 'cantidad': 0, 'productos': []},
                'tarjetas_credito': {'total': 0, 'cantidad': 0, 'productos': []},
                'prestamos': {'total': 0, 'cantidad': 0, 'productos': []},
                'fondos_inversion': {'total': 0, 'cantidad': 0, 'productos': []},
                'total_patrimonio': 0
            }
        
        # Agrupar por tipo de producto
        resumen = {
            'cuentas_bancarias': {'total': 0, 'cantidad': 0, 'productos': []},
            'tarjetas_credito': {'total': 0, 'cantidad': 0, 'productos': []},
            'prestamos': {'total': 0, 'cantidad': 0, 'productos': []},
            'fondos_inversion': {'total': 0, 'cantidad': 0, 'productos': []}
        }
        
        for producto in productos:
            tipo = producto['tipo_producto']
            if tipo == 'cuenta_bancaria':
                resumen['cuentas_bancarias']['productos'].append(producto)
                resumen['cuentas_bancarias']['total'] += producto['valor_efectivo']
                resumen['cuentas_bancarias']['cantidad'] += 1
            elif tipo == 'tarjeta_credito':
                resumen['tarjetas_credito']['productos'].append(producto)
                resumen['tarjetas_credito']['total'] += producto['valor_efectivo']
                resumen['tarjetas_credito']['cantidad'] += 1
            elif tipo == 'prestamo':
                resumen['prestamos']['productos'].append(producto)
                resumen['prestamos']['total'] += abs(producto['valor_efectivo'])  # Mostrar como positivo
                resumen['prestamos']['cantidad'] += 1
            elif tipo == 'fondo_inversion':
                resumen['fondos_inversion']['productos'].append(producto)
                resumen['fondos_inversion']['total'] += producto['valor_efectivo']
                resumen['fondos_inversion']['cantidad'] += 1
        
        # Calcular patrimonio total (activos - pasivos)
        patrimonio_positivo = (resumen['cuentas_bancarias']['total'] + 
                              resumen['fondos_inversion']['total'] +
                              resumen['tarjetas_credito']['total'])
        patrimonio_negativo = resumen['prestamos']['total']
        
        resumen['total_patrimonio'] = patrimonio_positivo - patrimonio_negativo
        
        return resumen
        
    except Exception as e:
        print(f"Error al obtener resumen de productos del usuario {user_id}: {str(e)}")
        return {
            'cuentas_bancarias': {'total': 0, 'cantidad': 0, 'productos': []},
            'tarjetas_credito': {'total': 0, 'cantidad': 0, 'productos': []},
            'prestamos': {'total': 0, 'cantidad': 0, 'productos': []},
            'fondos_inversion': {'total': 0, 'cantidad': 0, 'productos': []},
            'total_patrimonio': 0
        }

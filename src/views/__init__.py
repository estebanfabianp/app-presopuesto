"""
Componentes UI Reutilizables

Este paquete contiene todos los componentes de interfaz de usuario que pueden
ser reutilizados a través de diferentes vistas de la aplicación.

Componentes disponibles:
    - sidebar: Menú lateral de navegación principal
    - tables: Componentes de tablas de datos
    - charts: Componentes de gráficos y visualizaciones
    - forms: Componentes de formularios reutilizables

Autor: [esteban patiño]
Fecha: [30-sep-2025]
Versión: 1.0
"""

from .sidebar import LeftSidebarMenu

__all__ = [
    'LeftSidebarMenu'
]

# 👩‍💻 Guía de Desarrollo - App Presupuesto v0.7.1
**Sistema Empresarial de Gestión Financiera**

## 🚀 Quick Start

### Prerrequisitos
- Python 3.11+
- MySQL 8.0+ (REQUERIDO para funciones empresariales)
- Flet framework
- IDE recomendado: VS Code
- Git para control de versiones

### Setup Inicial (< 30 minutos)
```bash
# 1. Clonar repositorio
git clone https://github.com/user/app-presopuesto
cd app-presupuesto

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Setup automático de base de datos (NUEVO)
# MÉTODO 1: Script maestro (recomendado)
cd base_de_datos/db/01_core/create
mysql -u root -p < 09_master_script.sql

# MÉTODO 2: Batch automático (Windows)
cd base_de_datos/db
init_db.bat

# 5. Verificar instalación
mysql -u root -p app_presupuesto -e "CALL sp_generar_reporte_documentacion();"

# 6. Ejecutar aplicación
python src/views/main.py
```

## 📋 Estándares de Código

### Patrón MVC Obligatorio
```python
# ✅ CORRECTO: Siguiendo patrón establecido
class CuentaController:
    def crear_cuenta(self, datos_cuenta):
        try:
            # 1. Validación robusta
            if not self._validar_datos(datos_cuenta):
                return {"error": "Datos inválidos"}
            
            # 2. Verificar permisos
            if not validar_sesion_y_permisos("crear_cuenta"):
                return {"error": "Sin permisos"}
            
            # 3. Lógica negocio
            resultado = self._procesar_cuenta(datos_cuenta)
            
            # 4. Logging automático
            self._log_operacion("cuenta_creada", resultado)
            
            return {"success": True, "data": resultado}
            
        except Exception as e:
            self._log_error("crear_cuenta", str(e))
            return {"error": "Error interno"}
```

### Documentación Obligatoria
```python
def obtener_cuenta_por_id(self, cuenta_id: int) -> Dict:
    """
    Obtiene una cuenta específica por su ID.
    
    Args:
        cuenta_id (int): ID único de la cuenta
        
    Returns:
        Dict: {
            "success": bool,
            "data": cuenta_object o None,
            "error": str opcional
        }
        
    Example:
        >>> controller = CuentaController()
        >>> result = controller.obtener_cuenta_por_id(123)
        >>> if result["success"]:
        >>>     cuenta = result["data"]
    """
```

## 🎯 Checklist Pre-Commit
- [ ] ✅ Código sigue patrón MVC establecido
- [ ] 📚 100% funciones públicas documentadas  
- [ ] 🔒 Validaciones seguridad implementadas
- [ ] ⚡ Performance <200ms operaciones críticas
- [ ] 🧪 Tests unitarios (coverage >85%)
- [ ] 📝 Logging apropiado errores y acciones

## 🔧 Herramientas Desarrollo
- **Linting**: flake8, black
- **Testing**: pytest
- **Performance**: cProfile para benchmarking
- **Database**: MySQL Workbench para schema changes

## 📞 Soporte
- **Lead**: Esteban Fabián Patiño Montealegre  
- **Email**: estebanfabianp@gmail.com
- **Response Time**: <24h para bloqueos críticos

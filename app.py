"""
Aplicación principal Flask para la migración a HTML
Punto de entrada para la aplicación web

Este archivo reemplazará a main.py (que usa Flet) cuando la migración esté completa.
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


def create_app(env='development'):
    """
    Factory para crear la aplicación Flask
    
    Args:
        env: 'development', 'testing', 'production'
    
    Returns:
        Flask app instance
    """
    
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'src', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'src', 'static')
    )
    
    # Cargar configuración
    from src.config import config
    app.config.from_object(config.get(env, config['default']))
    
    # Inicializar extensiones
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)
    
    # Registrar blueprints de rutas
    from src.routes import (
        auth,
        beneficiarios,
        categorias,
        cuentas_bancarias,
        constantes,
        dashboard,
        presupuesto,
        productos,
        transacciones,
        reportes,
        tarjetas,
        inversiones,
        metas,
        optimizacion_categorias,
        programadas,
        analisis,
    )
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(beneficiarios.bp)
    app.register_blueprint(categorias.bp)
    app.register_blueprint(cuentas_bancarias.bp)
    app.register_blueprint(constantes.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(presupuesto.bp)
    app.register_blueprint(transacciones.bp)
    app.register_blueprint(reportes.bp)
    app.register_blueprint(tarjetas.bp)
    app.register_blueprint(inversiones.bp)
    app.register_blueprint(metas.bp)
    app.register_blueprint(optimizacion_categorias.bp)
    app.register_blueprint(productos.bp)
    app.register_blueprint(programadas.bp)
    app.register_blueprint(analisis.bp)
    
    # Rutas de templates (pages, no API)
    @app.route('/')
    def index():
        """Página de inicio - redireccionar a login"""
        return redirect(url_for('login_page'))
    
    @app.route('/login')
    def login_page():
        """Página de login"""
        return render_template('auth/login.html')

    @app.route('/recuperar-password')
    def recover_password_page():
        """Página de recuperación de contraseña"""
        return render_template('auth/recover_password.html')
    
    @app.route('/dashboard')
    def dashboard_page():
        """Página del dashboard"""
        return render_template('dashboard/index.html')

    @app.route('/presupuesto')
    @app.route('/presupuestos')
    def presupuesto_page():
        """Página de presupuestos"""
        return render_template('presupuesto/index.html')

    @app.route('/transacciones')
    @app.route('/transacciones/historial')
    def transacciones_page():
        """Página de transacciones"""
        return render_template('transacciones/index.html')

    @app.route('/reportes')
    def reportes_page():
        """Página de reportes"""
        return render_template('reportes/index.html')

    @app.route('/tarjetas')
    def tarjetas_page():
        return render_template('tarjetas/index.html')

    @app.route('/inversiones')
    def inversiones_page():
        return render_template('inversiones/index.html')

    @app.route('/metas')
    def metas_page():
        return render_template('metas/index.html')

    @app.route('/productos')
    def productos_page():
        return render_template('productos/index.html')

    @app.route('/cuentas-bancarias')
    def cuentas_bancarias_page():
        return render_template('cuentas_bancarias/index.html')

    @app.route('/beneficiarios')
    def beneficiarios_page():
        return render_template('beneficiarios/index.html')

    @app.route('/categorias')
    def categorias_page():
        return render_template('categorias/index.html')

    @app.route('/optimizacion-categorias')
    def optimizacion_categorias_page():
        return render_template('optimizacion_categorias/index.html')

    @app.route('/constantes')
    def constantes_page():
        return render_template('constantes/index.html')

    @app.route('/configuracion')
    @app.route('/notificaciones')
    def configuracion_page():
        return render_template('configuracion/index.html')

    @app.route('/perfil')
    def perfil_page():
        return render_template('perfil/index.html')

    @app.route('/programadas')
    def programadas_page():
        return render_template('programadas/index.html')

    @app.route('/analisis')
    def analisis_page():
        return render_template('analisis/index.html')

    @app.route('/exportar')
    def exportar_page():
        return render_template('exportar/index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        """Página no encontrada"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        """Error interno del servidor"""
        logger.error(f"Server error: {str(e)}")
        return render_template('errors/500.html'), 500
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        """Endpoint para verificar si la app está funcionando"""
        return {'status': 'ok', 'app': 'presopuesto-flask'}, 200
    
    logger.info(f"Flask app created in {env} environment")
    
    return app


if __name__ == "__main__":
    # Crear la app
    app = create_app(os.getenv('FLASK_ENV', 'development'))

    def _env_bool(name: str, default: bool) -> bool:
        raw = os.getenv(name)
        if raw is None:
            return default
        return str(raw).strip().lower() in {'1', 'true', 'yes', 'y', 'on'}
    
    # Ejecutar servidor
    app.run(
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=_env_bool('FLASK_DEBUG', True),
        use_reloader=_env_bool('FLASK_USE_RELOADER', False)
    )

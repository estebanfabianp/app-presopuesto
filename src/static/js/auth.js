/**
 * Gestión de autenticación y guardia de rutas
 */

class AuthManager {
    constructor() {
        this.user = null;
        this.isAuthenticated = false;
        this.publicRoutes = ['/login', '/registro', '/recuperar-password', '/'];
    }

    /**
     * Inicializar sesión al cargar la página
     */
    async initialize() {
        const token = localStorage.getItem('authToken');

        // Si no hay token, redirigir a login (excepto en rutas públicas)
        if (!token) {
            if (!this.isPublicRoute()) {
                window.location.href = '/login';
            }
            return;
        }

        // Intentar obtener usuario actual
        try {
            this.user = await api.getCurrentUser();
            this.isAuthenticated = true;
            this.setupUI();
        } catch (error) {
            console.error('Auth initialization failed:', error);
            localStorage.removeItem('authToken');
            if (!this.isPublicRoute()) {
                window.location.href = '/login';
            }
        }
    }

    /**
     * Verificar si la ruta actual es pública
     */
    isPublicRoute() {
        const currentPath = window.location.pathname;
        return this.publicRoutes.some(route => {
            if (route === '/') {
                return currentPath === '/';
            }
            return currentPath === route || currentPath.startsWith(route + '/');
        });
    }

    /**
     * Configurar UI con datos del usuario
     */
    setupUI() {
        // Actualizar saludo del usuario en navbar
        const userGreeting = document.getElementById('userGreeting');
        if (userGreeting && this.user) {
            const userName = this.user.nombre || this.user.email || 'Usuario';
            userGreeting.innerHTML = `<i class="fas fa-user-circle"></i> Bienvenido, ${userName}`;
        }

        // Configurar botón de logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }

        // Marcar link activo en menú
        this.highlightActiveNav();
    }

    /**
     * Resaltar el link activo en el menú lateral
     */
    highlightActiveNav() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.startsWith(href)) {
                link.classList.add('active');
            }
        });
    }

    /**
     * Cerrar sesión
     */
    async logout() {
        try {
            await api.logout();
        } catch (error) {
            console.warn('Logout error:', error);
        }
        this.isAuthenticated = false;
        this.user = null;
        window.location.href = '/login';
    }

    /**
     * Verificar si el usuario está autenticado
     */
    isLoggedIn() {
        return this.isAuthenticated && !!localStorage.getItem('authToken');
    }
}

// Instancia global del gestor de autenticación
const auth = new AuthManager();

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    auth.initialize();
});

// Manejo global de errores no capturados
window.addEventListener('unhandledrejection', event => {
    if (event.reason instanceof Error) {
        console.error('Unhandled error:', event.reason);
        
        // Si es un error de autenticación y no estamos en login
        if (event.reason.message.includes('Unauthorized') || 
            event.reason.message.includes('expirada')) {
            showToast('Tu sesión ha expirado. Por favor inicia sesión de nuevo.', 'warning');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        }
    }
});

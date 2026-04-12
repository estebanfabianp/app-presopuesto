/**
 * API Client para comunicación con backend Flask
 * Maneja autenticación, errores y formatos de datos
 */

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.token = this.getToken();
    }

    /**
     * Obtener token de localStorage
     */
    getToken() {
        return localStorage.getItem('authToken');
    }

    /**
     * Guardar token en localStorage
     */
    setToken(token) {
        localStorage.setItem('authToken', token);
        this.token = token;
    }

    /**
     * Limpiar token
     */
    clearToken() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
        this.token = null;
    }

    /**
     * Realizar solicitud HTTP
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Agregar autorización si hay token
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        // Agregar body para métodos que lo soportan
        if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);

            // Manejo de respuesta no autorizada
            if (response.status === 401 && endpoint !== '/auth/login') {
                this.clearToken();
                window.location.href = '/login';
                throw new Error('Sesión expirada. Por favor inicia sesión nuevamente.');
            }

            // Intentar parsear JSON
            let responseData;
            const contentType = response.headers.get('content-type');
            if (contentType?.includes('application/json')) {
                responseData = await response.json();
            } else {
                responseData = await response.text();
            }

            // Manejo de errores HTTP
            if (!response.ok) {
                const error = new Error(responseData.message || 'Error en la solicitud');
                error.status = response.status;
                error.data = responseData;
                throw error;
            }

            return responseData;

        } catch (error) {
            console.error(`API Error [${method} ${endpoint}]:`, error);
            throw error;
        }
    }

    // ==================== AUTENTICACIÓN ====================
    
    /**
     * Iniciar sesión
     */
    async login(email, password) {
        const response = await this.request('POST', '/auth/login', { email, password });
        this.setToken(response.token);
        return response;
    }

    /**
     * Cerrar sesión
     */
    async logout() {
        try {
            await this.request('POST', '/auth/logout');
        } catch (error) {
            console.warn('Logout error (ignorado):', error);
        }
        this.clearToken();
    }

    /**
     * Obtener usuario actual autenticado
     */
    async getCurrentUser() {
        return this.request('GET', '/auth/me');
    }

    // ==================== DASHBOARD ====================
    
    /**
     * Obtener resumen del dashboard
     */
    async getDashboardSummary() {
        return this.request('GET', '/dashboard/summary');
    }

    /**
     * Obtener gastos por categoría
     */
    async getGastosPorCategoria() {
        return this.request('GET', '/dashboard/gastos-por-categoria');
    }

    // ==================== PRESUPUESTO ====================
    
    /**
     * Obtener lista de presupuestos
     */
    async getPresupuestos(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request('GET', `/presupuesto${queryString ? '?' + queryString : ''}`);
    }

    /**
     * Obtener un presupuesto por ID
     */
    async getPresupuesto(id) {
        return this.request('GET', `/presupuesto/${id}`);
    }

    /**
     * Crear nuevo presupuesto
     */
    async createPresupuesto(data) {
        return this.request('POST', '/presupuesto', data);
    }

    /**
     * Actualizar presupuesto
     */
    async updatePresupuesto(id, data) {
        return this.request('PUT', `/presupuesto/${id}`, data);
    }

    /**
     * Eliminar presupuesto
     */
    async deletePresupuesto(id) {
        return this.request('DELETE', `/presupuesto/${id}`);
    }

    // ==================== TRANSACCIONES ====================
    
    /**
     * Obtener lista de transacciones
     */
    async getTransacciones(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request('GET', `/transacciones${queryString ? '?' + queryString : ''}`);
    }

    /**
     * Crear nueva transacción
     */
    async createTransaccion(data) {
        return this.request('POST', '/transacciones', data);
    }

    /**
     * Actualizar transacción
     */
    async updateTransaccion(id, data) {
        return this.request('PUT', `/transacciones/${id}`, data);
    }

    /**
     * Eliminar transacción
     */
    async deleteTransaccion(id) {
        return this.request('DELETE', `/transacciones/${id}`);
    }

    // ==================== REPORTES ====================
    
    /**
     * Obtener datos de reportes
     */
    async getReporteData(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request('GET', `/reportes/data${queryString ? '?' + queryString : ''}`);
    }

    // ==================== TARJETAS ====================

    /**
     * Obtener resumen del módulo tarjetas
     */
    async getTarjetasSummary() {
        return this.request('GET', '/tarjetas/summary');
    }

    // ==================== INVERSIONES ====================

    /**
     * Obtener resumen del módulo inversiones
     */
    async getInversionesSummary() {
        return this.request('GET', '/inversiones/summary');
    }

    // ==================== METAS ====================

    /**
     * Obtener resumen del módulo metas
     */
    async getMetasSummary() {
        return this.request('GET', '/metas/summary');
    }
}

// Instancia global del cliente API
const api = new APIClient();

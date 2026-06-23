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
     * Registrar usuario nuevo
     */
    async register(nombre, email, password, telefono = null) {
        const payload = { nombre, email, password };
        if (telefono) {
            payload.telefono = telefono;
        }
        const response = await this.request('POST', '/auth/register', payload);
        if (response?.token) {
            this.setToken(response.token);
        }
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
     * Obtener dashboard extendido (KPIs, alertas, rankings, compromisos)
     */
    async getDashboardOverview() {
        return this.request('GET', '/dashboard/overview');
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

    /**
     * Obtener hoja de presupuesto anual o mensual.
     */
    async getPresupuestoSheet(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request('GET', `/presupuesto/hoja${queryString ? '?' + queryString : ''}`);
    }

    /**
     * Guardar hoja de presupuesto con líneas de detalle.
     */
    async savePresupuestoSheet(data) {
        return this.request('POST', '/presupuesto/hoja', data);
    }

    /**
     * Derivar presupuesto mensual desde el anual del mismo año.
     */
    async deriveMonthlyBudget(data) {
        return this.request('POST', '/presupuesto/hoja/derivar', data);
    }

    /**
     * Obtener categorías en formato plano.
     */
    async getCategoriasFlat(params = {}) {
        const queryString = new URLSearchParams({ plana: 'true', ...params }).toString();
        return this.request('GET', `/categorias?${queryString}`);
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

    /**
     * Obtener catalogos para importacion ETL de transacciones.
     */
    async getTransaccionesImportCatalogos() {
        return this.request('GET', '/transacciones/import/catalogos');
    }

    /**
     * Subir archivo para importacion ETL de transacciones.
     */
    async uploadTransaccionesImport(formData) {
        const headers = {};
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        let response;
        try {
            response = await fetch(`${this.baseURL}/transacciones/import/upload`, {
                method: 'POST',
                headers,
                body: formData,
            });
        } catch (networkError) {
            const error = new Error(
                'No se pudo conectar con el servidor durante la importación (verifica que la app siga activa en /health).'
            );
            error.cause = networkError;
            throw error;
        }

        const contentType = response.headers.get('content-type') || '';
        const payload = contentType.includes('application/json')
            ? await response.json()
            : { message: await response.text() };

        if (!response.ok) {
            let message = payload.message || 'Error en importacion ETL';
            if (Array.isArray(payload.errors) && payload.errors.length) {
                message = `${message}: ${payload.errors.join('; ')}`;
            }
            const error = new Error(message);
            error.status = response.status;
            error.data = payload;
            throw error;
        }

        return payload;
    }

    /**
     * Descargar plantilla ETL por fuente.
     */
    getTransaccionesTemplateUrl(source) {
        return `${this.baseURL}/transacciones/import/template?source=${encodeURIComponent(source)}`;
    }

    // ==================== REPORTES ====================
    
    /**
     * Obtener datos de reportes
     */
    async getReporteData(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request('GET', `/reportes/data${queryString ? '?' + queryString : ''}`);
    }

    /**
     * Obtener suite consolidada de reportes (flujo, uso, cuentas y presupuesto).
     */
    async getReporteSuite(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request('GET', `/reportes/suite${queryString ? '?' + queryString : ''}`);
    }

    /**
     * Obtener metadata para filtros globales de reportes.
     */
    async getReporteMetadata() {
        return this.request('GET', '/reportes/metadata');
    }

    /**
     * Obtener detalle de movimientos para drill-down desde graficos.
     */
    async getReporteDetalleMovimientos(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request('GET', `/reportes/detalle-movimientos${queryString ? '?' + queryString : ''}`);
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

/**
 * Utilidades comunes para JavaScript
 */

/**
 * Formatear cantidad como moneda
 */
function formatCurrency(amount, currency = 'COP') {
    try {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount || 0);
    } catch (error) {
        console.warn('Currency format error:', error);
        return `$${(amount || 0).toFixed(2)}`;
    }
}

/**
 * Formatear fecha
 */
function formatDate(date, format = 'dd/MM/yyyy') {
    if (!date) return '';
    
    try {
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';
        
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        
        return format
            .replace('dd', day)
            .replace('MM', month)
            .replace('yyyy', year)
            .replace('HH', hours)
            .replace('mm', minutes);
    } catch (error) {
        console.warn('Date format error:', error);
        return '';
    }
}

/**
 * Mostrar toast (notificación temporal)
 */
function showToast(message, type = 'info', duration = 5000) {
    let toastContainer = document.getElementById('toastContainer');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.role = 'alert';
    toast.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove después del tiempo especificado
    if (duration > 0) {
        setTimeout(() => {
            toast.remove();
        }, duration);
    }
    
    return toast;
}

/**
 * Mostrar spinner global de carga
 */
function showSpinner(show = true) {
    let spinner = document.getElementById('globalSpinner');
    
    if (show && !spinner) {
        spinner = document.createElement('div');
        spinner.id = 'globalSpinner';
        spinner.innerHTML = `
            <div class="spinner-overlay">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2 text-muted">Cargando...</p>
            </div>
        `;
        document.body.appendChild(spinner);
        return;
    }
    
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}

/**
 * Validar email
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validar contraseña
 */
function isValidPassword(password) {
    // Al menos 6 caracteres
    return password && password.length >= 6;
}

/**
 * Deep copy (clonación profunda) de objeto
 */
function deepCopy(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Verificar si un objeto está vacío
 */
function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

/**
 * Agregar clase con delay
 */
function addClassWithDelay(element, className, delay = 0) {
    if (delay > 0) {
        setTimeout(() => element.classList.add(className), delay);
    } else {
        element.classList.add(className);
    }
}

/**
 * Remover clase con delay
 */
function removeClassWithDelay(element, className, delay = 0) {
    if (delay > 0) {
        setTimeout(() => element.classList.remove(className), delay);
    } else {
        element.classList.remove(className);
    }
}

/**
 * Debounce - ejecutar función después de X ms sin eventos
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle - ejecutar función máximo cada X ms
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Confirmar acción antes de ejecutar
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Copiar texto al portapapeles
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copiado al portapapeles', 'success', 3000);
        return true;
    } catch (error) {
        console.error('Copy error:', error);
        showToast('Error al copiar', 'danger');
        return false;
    }
}

/**
 * Descargar archivo
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Obtener parámetro de URL
 */
function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Esperar N milisegundos
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Convertir objeto a query string
 */
function toQueryString(obj) {
    return Object.keys(obj)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key])}`)
        .join('&');
}

/**
 * Capitalizar primera letra
 */
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncar texto
 */
function truncate(str, length = 50, suffix = '...') {
    if (!str || str.length <= length) return str;
    return str.substring(0, length) + suffix;
}

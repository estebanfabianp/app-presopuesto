/**
 * Test Script para validar la interfaz de presupuesto
 * Ejecutar en la consola del navegador en http://127.0.0.1:5000/presupuesto
 */

// Test 1: Verificar que el objeto api existe
console.log("=== TEST 1: API Wrapper ===");
console.log("API exists:", typeof api !== 'undefined');
console.log("API methods:", Object.keys(api));

// Test 2: Verificar funciones de formateo
console.log("\n=== TEST 2: Format Functions ===");
console.log("formatCurrency(1000):", formatCurrency(1000));
console.log("formatDate('2026-01-15'):", formatDate('2026-01-15'));

// Test 3: Verificar que los elementos del DOM existen
console.log("\n=== TEST 3: DOM Elements ===");
const elementsToCheck = [
    'selAño', 'containerAnuales', 'containerMensuales',
    'modalPresupuestoAnual', 'modalPresupuestoMensual', 'modalDuplicarAnual',
    'presAnualNombre', 'presAnualMonto', 'presMensualNombre', 'presMensualMonto',
    'btnGuardarAnual', 'btnGuardarMensual', 'btnDuplicarAnual'
];

elementsToCheck.forEach(id => {
    const elem = document.getElementById(id);
    console.log(`${id}: ${elem ? '✓' : '✗ MISSING'}`);
});

// Test 4: Verificar el contenido de estado
console.log("\n=== TEST 4: State ===");
console.log("presupuestosAnuales:", presupuestosAnuales);
console.log("presupuestosMensuales:", presupuestosMensuales);

// Test 5: Intentar hacer una llamada a la API
console.log("\n=== TEST 5: API Call ===");
api.getPresupuestos()
    .then(datos => {
        console.log("✓ API Call successful");
        console.log("Presupuestos recibidos:", datos.length);
        console.log("Primera línea:", datos[0] || 'No data');
    })
    .catch(err => {
        console.log("✗ API Call failed:", err.message);
    });

// Test 6: Mostrar un toast de prueba
console.log("\n=== TEST 6: Toast ===");
showToast('Esto es un mensaje de prueba', 'info');
setTimeout(() => {
    showToast('Presupuesto guardado sin errores', 'success');
}, 2000);

console.log("\n=== TESTS COMPLETE ===");

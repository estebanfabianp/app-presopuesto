import requests

base = 'http://127.0.0.1:5000'
login = requests.post(f'{base}/api/auth/login', json={'email':'esteban@email.com','password':'123456'})
token = login.json().get('token','')

# Get page with improved UI
page = requests.get(f'{base}/tarjetas', cookies={'access_token_cookie': token})
print(f'Page status: {page.status_code}')

# Check for new UI elements
checks = [
    ('modalDetalleDiferido', 'Modal de detalle'),
    ('abrirDetalleDiferido', 'Función JavaScript'),
    ('amortTable', 'Tabla de amortización'),
    ('pagosTable', 'Tabla de pagos'),
    ('tab-amort', 'Pestaña amortización'),
    ('tab-pagos', 'Pestaña pagos'),
    ('detDesc', 'Campo descripción'),
    ('detSaldoPendiente', 'Campo saldo pendiente'),
]

print('\n=== VALIDACIÓN DE UI ===')
for elem, desc in checks:
    present = elem in page.text
    status = '✓' if present else '✗'
    print(f'{status} {desc}: {elem}')

# Test the API endpoint with detalle data
print('\n=== TEST ENDPOINT DETALLE ===')
r = requests.get(f'{base}/api/tarjetas/diferidos/2/detalle', 
                 headers={'Authorization': f'Bearer {token}'})
print(f'GET /diferidos/2/detalle: {r.status_code}')
if r.ok:
    data = r.json()
    print(f'  - Descripción: {data.get("descripcion")}')
    print(f'  - Cuotas en amortización: {len(data.get("amortizacion", []))}')
    print(f'  - Pagos registrados: {len(data.get("historico_pagos", []))}')

print('\n=== RESUMEN ===')
all_checks = all(elem in page.text for elem, _ in checks)
print(f'UI completa: {"✓ SÍ" if all_checks else "✗ NO"}')

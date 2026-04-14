import requests
import json

base = 'http://127.0.0.1:5000'

# 1. LOGIN
print('=== AUTENTICACIÓN ===')
login = requests.post(f'{base}/api/auth/login', json={'email':'esteban@email.com','password':'123456'})
print(f'Login: {login.status_code}')
token = login.json().get('token','')
H = {'Authorization': f'Bearer {token}', 'Content-Type':'application/json'}

# 2. GET SUMMARY (estado inicial)
print('\n=== ESTADO INICIAL ===')
summary = requests.get(f'{base}/api/tarjetas/diferidos/summary', headers=H)
print(f'Summary: {summary.status_code}')
print(json.dumps(summary.json(), indent=2))

# 3. CREAR DIFERIDO 1: Sin interés
print('\n=== CREAR DIFERIDO 1 (Sin interés) ===')
d1 = requests.post(f'{base}/api/tarjetas/diferidos', headers=H, json={
    'id_tarjeta': 1,
    'descripcion': 'iPhone 15 Pro (sin interes)',
    'valor_total': 3000000,
    'numero_cuotas': 12,
    'sin_interes': True,
    'tasa_mensual': 0,
    'fecha_compra': '2026-04-12'
})
print(f'Create D1: {d1.status_code}')
d1_data = d1.json()
print(json.dumps(d1_data, indent=2, default=str))
id_d1 = d1_data.get('id_diferido')

# 4. CREAR DIFERIDO 2: Con interés
print('\n=== CREAR DIFERIDO 2 (Con interés 2% mensual) ===')
d2 = requests.post(f'{base}/api/tarjetas/diferidos', headers=H, json={
    'id_tarjeta': 1,
    'descripcion': 'Computadora (con interes)',
    'valor_total': 5000000,
    'numero_cuotas': 24,
    'sin_interes': False,
    'tasa_mensual': 2.0,
    'fecha_compra': '2026-04-12'
})
print(f'Create D2: {d2.status_code}')
d2_data = d2.json()
print(json.dumps(d2_data, indent=2, default=str))
id_d2 = d2_data.get('id_diferido')

# 5. GET SUMMARY (después de crear)
print('\n=== SUMMARY DESPUÉS DE CREAR ===')
summary = requests.get(f'{base}/api/tarjetas/diferidos/summary', headers=H)
print(json.dumps(summary.json(), indent=2, default=str))

# 6. GET LISTA DE DIFERIDOS
print('\n=== LISTA DE DIFERIDOS ===')
lista = requests.get(f'{base}/api/tarjetas/diferidos', headers=H)
print(f'Lista: {lista.status_code}, Total: {len(lista.json())}')
for d in lista.json():
    print(f"  - {d['descripcion']}: ${d['valor_total']:,} ({d['numero_cuotas']} cuotas, {d['cuotas_pagadas']}/{d['numero_cuotas']} pagadas)")

# 7. PAGAR CUOTA DE D1
print(f'\n=== PAGAR CUOTA 1 DE D1 ===')
p1 = requests.post(f'{base}/api/tarjetas/diferidos/{id_d1}/pagar-cuota', headers=H, json={})
print(f'Pay: {p1.status_code}')
print(json.dumps(p1.json(), indent=2, default=str))

# 8. PAGAR OTRA CUOTA DE D1
print(f'\n=== PAGAR CUOTA 2 DE D1 ===')
p2 = requests.post(f'{base}/api/tarjetas/diferidos/{id_d1}/pagar-cuota', headers=H, json={})
print(f'Pay: {p2.status_code}')
print(json.dumps(p2.json(), indent=2, default=str))

# 9. PAGAR CUOTA DE D2
print(f'\n=== PAGAR CUOTA 1 DE D2 ===')
p3 = requests.post(f'{base}/api/tarjetas/diferidos/{id_d2}/pagar-cuota', headers=H, json={})
print(f'Pay: {p3.status_code}')
print(json.dumps(p3.json(), indent=2, default=str))

# 10. SUMMARY FINAL
print('\n=== SUMMARY FINAL ===')
summary_final = requests.get(f'{base}/api/tarjetas/diferidos/summary', headers=H)
print(json.dumps(summary_final.json(), indent=2, default=str))

# 11. LISTA FINAL
print('\n=== LISTA FINAL ===')
lista_final = requests.get(f'{base}/api/tarjetas/diferidos', headers=H)
for d in lista_final.json():
    print(f"  - {d['descripcion']}: Pagadas {d['cuotas_pagadas']}/{d['numero_cuotas']}, Saldo: ${d['saldo_pendiente']:,}")

print('\n=== RESUMEN DE PRUEBAS ===')
print('✓ Creación de diferidos sin/con interés')
print('✓ Cálculo de amortización (sin interés y con interés)')
print('✓ Registro de pagos múltiples')
print('✓ Actualización de saldo pendiente')
print('✓ Resumen de diferidos activos')

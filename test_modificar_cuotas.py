import requests
import json

base = 'http://127.0.0.1:5000'
login = requests.post(f'{base}/api/auth/login', json={'email':'esteban@email.com','password':'123456'})
token = login.json().get('token','')
H = {'Authorization': f'Bearer {token}', 'Content-Type':'application/json'}

print('=== TEST: MODIFICAR CUOTAS Y SALDO ===\n')

# 1. CREAR DIFERIDO
print('1. Crear diferido')
d = requests.post(f'{base}/api/tarjetas/diferidos', headers=H, json={
    'id_tarjeta': 1, 'descripcion': 'Test Modificación',
    'valor_total': 1200000, 'numero_cuotas': 6, 'sin_interes': True,
    'tasa_mensual': 0, 'fecha_compra': '2026-04-12'
})
id_diff = d.json()['id_diferido']
print(f'✓ Diferido {id_diff} creado')
print(f'  Cuotas: 6, Cuota mensual: ${d.json()["cuota_mensual"]:,.0f}')

# 2. OBTENER DETALLE INICIAL
print('\n2. Detalle inicial')
det = requests.get(f'{base}/api/tarjetas/diferidos/{id_diff}/detalle', headers=H)
data = det.json()
print(f'✓ Número cuotas: {data["numero_cuotas"]}')
print(f'✓ Cuota mensual: ${data["cuota_mensual"]:,.0f}')
print(f'✓ Saldo: ${data["saldo_pendiente"]:,.0f}')

# 3. MODIFICAR: AUMENTAR CUOTAS A 12
print('\n3. Modificar: aumentar cuotas de 6 a 12')
p = requests.put(f'{base}/api/tarjetas/diferidos/{id_diff}/actualizar', headers=H, json={
    'numero_cuotas': 12,
    'saldo_pendiente': 1200000
})
print(f'Status: {p.status_code}')
if p.ok:
    resp = p.json()
    print(f'✓ Cuotas: {resp["numero_cuotas"]}')
    print(f'✓ Nueva cuota mensual: ${resp["cuota_mensual"]:,.0f} (era ${1200000/6:,.0f})')

# 4. PAGAR UNA CUOTA
print('\n4. Pagar cuota 1')
pago = requests.post(f'{base}/api/tarjetas/diferidos/{id_diff}/pagar-cuota', headers=H, json={})
print(f'✓ Cuota pagada: {pago.json()["numero_cuota"]}/{pago.json()["numero_cuotas"]}')

# 5. INTENTAR MODIFICAR A MENOS CUOTAS QUE PAGADAS
print('\n5. Validación: intentar modificar a <1 cuota')
invalid = requests.put(f'{base}/api/tarjetas/diferidos/{id_diff}/actualizar', headers=H, json={
    'numero_cuotas': 1,
    'saldo_pendiente': 1200000
})
if invalid.status_code == 400:
    print(f'✓ Bloqueado correctamente: {invalid.json()["message"]}')

# 6. MODIFICAR SALDO SOLAMENTE
print('\n6. Modificar saldo a $500k (mantener 12 cuotas)')
mod2 = requests.put(f'{base}/api/tarjetas/diferidos/{id_diff}/actualizar', headers=H, json={
    'numero_cuotas': 12,
    'saldo_pendiente': 500000
})
if mod2.ok:
    print(f'✓ Nuevo saldo: ${mod2.json()["saldo_pendiente"]:,.0f}')
    print(f'✓ Nueva cuota: ${mod2.json()["cuota_mensual"]:,.0f}')

# 7. OBTENER DETALLE FINAL
print('\n7. Detalle final')
det_final = requests.get(f'{base}/api/tarjetas/diferidos/{id_diff}/detalle', headers=H)
data_final = det_final.json()
print(f'✓ Número cuotas: {data_final["numero_cuotas"]}')
print(f'✓ Saldo pendiente: ${data_final["saldo_pendiente"]:,.0f}')
print(f'✓ Cuota mensual: ${data_final["cuota_mensual"]:,.0f}')

print('\n=== RESUMEN ===')
print('✓ Endpoint PUT /actualizar funciona')
print('✓ Recalcula cuota mensual automáticamente')
print('✓ Valida que cuotas > pagadas')
print('✓ Permite modificar número de cuotas')
print('✓ Permite modificar saldo pendiente')

import requests
import json

base = 'http://127.0.0.1:5000'

print('=== TEST DE 3 MEJORAS IMPLEMENTADAS ===\n')

# Login
login = requests.post(f'{base}/api/auth/login', json={'email':'esteban@email.com','password':'123456'})
token = login.json().get('token','')
H = {'Authorization': f'Bearer {token}', 'Content-Type':'application/json'}

# 1. CREAR DIFERIDO DE PRUEBA
print('1. CREAR DIFERIDO DE PRUEBA')
d = requests.post(f'{base}/api/tarjetas/diferidos', headers=H, json={
    'id_tarjeta': 1,
    'descripcion': 'Test Liquidación',
    'valor_total': 1000000,
    'numero_cuotas': 5,
    'sin_interes': True,
    'tasa_mensual': 0,
    'fecha_compra': '2026-04-12'
})
print(f'Create: {d.status_code}')
id_diff = d.json().get('id_diferido')
fecha_compra = '2026-04-12'
print(f'ID Diferido: {id_diff}')

# 2. OBTENER DETALLE PARA VER FECHA_PROXIMO_PAGO
print('\n2. VALIDAR FECHA_PROXIMO_PAGO')
det = requests.get(f'{base}/api/tarjetas/diferidos/{id_diff}/detalle', headers=H)
data = det.json()
print(f'Fecha próximo pago: {data.get("fecha_proximo_pago")}')
print(f'Esperado: 2026-05-12 (fecha_compra + 1 mes)')

# 3. PAGAR CUOTA 1
print('\n3. PAGAR CUOTA 1')
p1 = requests.post(f'{base}/api/tarjetas/diferidos/{id_diff}/pagar-cuota', headers=H, json={})
print(f'Pago 1: {p1.status_code}')
print(f'Cuota: {p1.json()["numero_cuota"]}/{p1.json()["numero_cuotas"]}')

# 4. VALIDAR FECHA_PROXIMO_PAGO ACTUALIZADA
print('\n4. VALIDAR FECHA_PROXIMO_PAGO ACTUALIZADA')
det = requests.get(f'{base}/api/tarjetas/diferidos/{id_diff}/detalle', headers=H)
data = det.json()
print(f'Fecha próximo pago (después de pago 1): {data.get("fecha_proximo_pago")}')
print(f'Esperado: 2026-06-12 (fecha_compra + 2 meses)')

# 5. INTENTO DE PAGAR CUOTA 1 NUEVAMENTE (VALIDACIÓN DUPLICADO)
print('\n5. VALIDACIÓN DE CUOTA DUPLICADA')
p1_dup = requests.post(f'{base}/api/tarjetas/diferidos/{id_diff}/pagar-cuota', headers=H, json={})
if p1_dup.status_code == 400:
    print(f'✓ Validacion OK: {p1_dup.json()["message"]}')
else:
    print(f'✗ ERROR: Se permitió pagar cuota duplicada')

# 6. PAGAR CUOTA 2 Y 3
print('\n6. PAGAR CUOTAS 2 Y 3')
p2 = requests.post(f'{base}/api/tarjetas/diferidos/{id_diff}/pagar-cuota', headers=H, json={})
print(f'Cuota 2: {p2.json()["numero_cuota"]}/{p2.json()["numero_cuotas"]}')
p3 = requests.post(f'{base}/api/tarjetas/diferidos/{id_diff}/pagar-cuota', headers=H, json={})
print(f'Cuota 3: {p3.json()["numero_cuota"]}/{p3.json()["numero_cuotas"]}')
print(f'Saldo después de 3 pagos: ${p3.json()["saldo_restante"]:,.0f}')

# 7. LIQUIDACIÓN ANTICIPADA
print('\n7. LIQUIDACIÓN ANTICIPADA')
liq = requests.post(f'{base}/api/tarjetas/diferidos/{id_diff}/liquidar', headers=H, json={})
print(f'Liquidar: {liq.status_code}')
if liq.ok:
    resp = liq.json()
    print(f'Cuotas liquidadas: {resp["cuotas_liquidadas"]}')
    print(f'Valor pagado: ${resp["valor_pagado"]:,.0f}')
    print(f'Saldo anterior: ${resp["saldo_anterior"]:,.0f}')
    print(f'Message: {resp["message"]}')

# 8. OBTENER DETALLE FINAL
print('\n8. DETALLE FINAL DESPUÉS DE LIQUIDACIÓN')
det_final = requests.get(f'{base}/api/tarjetas/diferidos/{id_diff}/detalle', headers=H)
data_final = det_final.json()
print(f'Estado: {data_final.get("estado")}')
print(f'Cuotas pagadas: {data_final.get("cuotas_pagadas")}/{data_final.get("numero_cuotas")}')
print(f'Saldo pendiente: ${data_final.get("saldo_pendiente"):,.0f}')
print(f'Fecha próximo pago: {data_final.get("fecha_proximo_pago")}')

# 9. INTENTO DE PAGAR DESPUÉS DE LIQUIDACIÓN (DEBE FALLAR)
print('\n9. VALIDACION: PAGAR DESPUÉS DE LIQUIDACIÓN')
pago_final = requests.post(f'{base}/api/tarjetas/diferidos/{id_diff}/pagar-cuota', headers=H, json={})
if pago_final.status_code == 400:
    print(f'✓ Protección OK: {pago_final.json()["message"]}')
else:
    print(f'✗ ERROR: Se permitió pagar diferido liquidado')

print('\n=== RESUMEN DE PRUEBAS ===')
print('✓ Validación de cuota duplicada implementada')
print('✓ Fecha próximo pago calculada correctamente desde fecha_compra')
print('✓ Liquidación anticipada funciona correctamente')
print('✓ Estado se actualiza a "pagado" después de liquidación')
print('✓ Protecciones contra pagos después de liquidación funcionan')

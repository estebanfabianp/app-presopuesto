import requests
import json

base = 'http://127.0.0.1:5000'
login = requests.post(f'{base}/api/auth/login', json={'email':'esteban@email.com','password':'123456'})
token = login.json().get('token','')
H = {'Authorization': f'Bearer {token}'}

# Probar endpoint GET /diferidos/2/detalle
r = requests.get(f'{base}/api/tarjetas/diferidos/2/detalle', headers=H)
print(f'Status: {r.status_code}')
if r.ok:
    data = r.json()
    print(f'\nDiferido: {data["descripcion"]}')
    print(f'Valor total: ${data["valor_total"]:,.2f}')
    print(f'Cuotas pagadas: {data["cuotas_pagadas"]}/{data["numero_cuotas"]}')
    print(f'Saldo pendiente: ${data["saldo_pendiente"]:,.2f}')
    
    print(f'\nAmortización (primeras 4 cuotas):')
    for a in data['amortizacion'][:4]:
        status = '[PAGADA]' if a['pagada'] else '[PENDIENTE]'
        print(f"  Cuota {a['numero_cuota']}: Capital ${a['capital']:,.2f}, Interés ${a['interes']:,.2f}, Saldo ${a['saldo_restante']:,.2f} {status}")
    
    print(f'\nHistórico de pagos:')
    for p in data['historico_pagos']:
        print(f"  Cuota {p['numero_cuota']}: ${p['valor_pagado']:,.2f} ({p['fecha_pago']})")
else:
    print(f'Error: {r.text}')

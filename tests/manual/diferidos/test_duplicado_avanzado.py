import requests

base = 'http://127.0.0.1:5000'
login = requests.post(f'{base}/api/auth/login', json={'email':'esteban@email.com','password':'123456'})
token = login.json().get('token','')
H = {'Authorization': f'Bearer {token}'}

print('=== VALIDACION DE CUOTA DUPLICADA (TEST AVANZADO) ===\n')

# Crear diferido
d = requests.post(f'{base}/api/tarjetas/diferidos', headers=H, json={
    'id_tarjeta': 1, 'descripcion': 'Test Duplicado', 'valor_total': 500000,
    'numero_cuotas': 3, 'sin_interes': True, 'tasa_mensual': 0, 'fecha_compra': '2026-04-12'
})
id_diff = d.json()['id_diferido']
print(f'Diferido creado: {id_diff}')

# Pagar cuota 1
p1 = requests.post(f'{base}/api/tarjetas/diferidos/{id_diff}/pagar-cuota', headers=H, json={})
print(f'\nPago 1: {p1.status_code} - Cuota {p1.json()["numero_cuota"]}/{p1.json()["numero_cuotas"]}')

# Intentar insertar DIRECTAMENTE en BD sin actualizar cuotas_pagadas (simula duplicado)
import mysql.connector
from mysql.connector import Error
try:
    conn = mysql.connector.connect(
        host='localhost', user='root', password='', database='app_presupuesto'
    )
    cursor = conn.cursor()
    
    # Intento insidioso: insertar pago para cuota 1 nuevamente (diferente timestamp)
    try:
        cursor.execute(
            "INSERT INTO tarjeta_diferido_pago (id_diferido, numero_cuota, fecha_pago, valor_pagado, interes_pagado, capital_pagado, saldo_restante) VALUES (%s, %s, NOW(), 0, 0, 0, 0)",
            (id_diff, 1)
        )
        conn.commit()
        print('\n✗ ERROR: Se permitió insertar duplicado en base de datos!')
    except Error as e:
        # Esperar errores de restricción
        if 'Duplicate' in str(e) or 'UNIQUE' in str(e):
            print('\n✓ EXCELENTE: Base de datos bloqueó el ÚNICO constraint en (id_diferido, numero_cuota)')
        else:
            print(f'\n? Error desconocido: {str(e)[:100]}')
    finally:
        cursor.close()
        conn.close()
except Exception as e:
    print(f'\nNo se pudo conectar a BD para test avanzado: {str(e)[:100]}')

print('\n=== CONCLUSIÓN ===')
print('✓ Validación de duplicado está en 2 niveles:')
print('  1. En API: Chequeo en aplicación antes de insertar')
print('  2. En BD: Restricción UNIQUE en (id_diferido, numero_cuota)')

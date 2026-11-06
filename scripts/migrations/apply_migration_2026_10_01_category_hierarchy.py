#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Organiza la tabla categoria en jerarquía por categorías principales y subcategorías."""

import mysql.connector


def main():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='app_presupuesto',
        port=3306,
        autocommit=False,
    )
    cur = conn.cursor()
    roots = [
        'Ingresos',
        'Vivienda',
        'Alimentación',
        'Transporte',
        'Salud',
        'Educación',
        'Entretenimiento',
        'Finanzas',
        'Ahorro e inversión',
        'Hogar y personales',
    ]

    created = {}
    try:
        for name in roots:
            cur.execute('SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s) LIMIT 1', (name,))
            row = cur.fetchone()
            if row:
                created[name] = row[0]
                continue
            cur.execute(
                'INSERT INTO categoria (nombre, parent_id, estado, icono, color) VALUES (%s, NULL, 1, %s, %s)',
                (name, 'fa-tag', '#6c757d'),
            )
            created[name] = cur.lastrowid

        mapping = {
            'Ingresos': ['Salario', 'Bonificaciones', 'Freelance/Trabajos Independientes', 'Inversiones', 'Dividendos', 'Intereses Bancarios', 'Alquiler de Propiedades', 'Ventas', 'Subsidios', 'Pensión', 'Otros Ingresos'],
            'Vivienda': ['Vivienda - Arriendo/Hipoteca', 'Servicios Públicos', 'Internet y Telefonía', 'Seguros', 'Mantenimiento del Hogar', 'Reparaciones', 'Decoración'],
            'Alimentación': ['Alimentación', 'Supermercado', 'Restaurantes', 'Café y Snacks', 'Domicilios', 'Mercado Libre', 'Comer afuera'],
            'Transporte': ['Transporte', 'Transporte Público', 'Gasolina/Combustible', 'Moto - Gasolina, Mantenimiento, Accesorios, Seguridad', 'Taxi/Uber', 'Parqueadero'],
            'Salud': ['Salud - EPS/Medicina Prepagada', 'Medicamentos', 'Cuidado Personal', 'Gastos Médicos de Emergencia'],
            'Educación': ['Educación', 'Libros y Revistas'],
            'Entretenimiento': ['Entretenimiento', 'Deportes y Gimnasio', 'Hobbies', 'Viajes y Vacaciones', 'Cine y Teatro', 'Música y Streaming'],
            'Finanzas': ['Préstamos y Deudas', 'Impuestos', 'Transferencias entre cuentas', 'Pagos de Tarjeta de Crédito', 'Retiros en Efectivo', 'Comisiones Bancarias', 'Transferencias a Nequi', 'Crédito', 'Abono al banco', 'IVA'],
            'Ahorro e inversión': ['Ahorro de Emergencia', 'Ahorro para Objetivos', 'Inversiones en Acciones', 'Inversiones en Fondos', 'CDT y Cuentas de Ahorro', 'Pensiones Voluntarias'],
            'Hogar y personales': ['Ropa y Calzado', 'Regalos', 'Donaciones', 'Mascota', 'Licor', 'Cuota de manejo', 'Comunicaciones', 'Transferencia a fondo'],
        }

        for parent_name, names in mapping.items():
            parent_id = created[parent_name]
            for name in names:
                cur.execute('SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s) LIMIT 1', (name,))
                row = cur.fetchone()
                if not row:
                    continue
                cat_id = row[0]
                if cat_id == parent_id:
                    continue
                cur.execute('UPDATE categoria SET parent_id = %s WHERE id_categoria = %s', (parent_id, cat_id))

        conn.commit()
        print('ROOT_CATEGORIES:', created)
        print('OK')
    except Exception as exc:
        conn.rollback()
        print(f'ERROR: {exc}')
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()

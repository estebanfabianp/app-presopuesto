#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normaliza los nombres de la tabla categoria y corrige textos con mojibake."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector


def clean_category_names():
    db = DatabaseConnector()
    if not db.conn:
        raise RuntimeError('No se pudo conectar a la base de datos')

    corrections = {
        51: 'Transferencias entre cuentas',
        57: 'Sin categorizar',
        58: 'Mascota',
        59: 'Corte de pelo',
        60: 'Comer afuera',
        61: 'Licor',
        62: 'Domicilios',
        63: 'Nequi',
        64: 'Cuota de manejo',
        65: 'Parqueadero',
        66: 'Mercado Libre',
        67: 'Transferencia a fondo',
        68: 'Abono al banco',
        69: 'IVA',
        70: 'Transferencias a Nequi',
        71: 'Crédito',
        72: 'Transporte',
        73: 'Alimentación',
        74: 'Comunicaciones',
        'Pensi├│n': 'Pensión',
        'Servicios P├║blicos': 'Servicios Públicos',
        'Internet y Telefon├¡a': 'Internet y Telefonía',
        'Educaci├│n': 'Educación',
        'Transporte P├║blico': 'Transporte Público',
        'Pr├®stamos y Deudas': 'Préstamos y Deudas',
        'Alimentaci├│n': 'Alimentación',
        'Caf├® y Snacks': 'Café y Snacks',
        'M├║sica y Streaming': 'Música y Streaming',
        'Tecnolog├¡a': 'Tecnología',
        'Decoraci├│n': 'Decoración',
        'Gastos M├®dicos de Emergencia': 'Gastos Médicos de Emergencia',
        'Bienes Ra├¡ces': 'Bienes Raíces',
        'Pagos de Tarjeta de Cr├®dito': 'Pagos de Tarjeta de Crédito',
        'Cr?dito': 'Crédito',
        'Alimentaci?n': 'Alimentación',
        'nequi': 'Nequi',
        'couta de manejo': 'Cuota de manejo',
        'corte de pelo': 'Corte de pelo',
        'comer afuera': 'Comer afuera',
        'domicilios': 'Domicilios',
        'transferencia a fondo': 'Transferencia a fondo',
        'abono al banco': 'Abono al banco',
        'iva': 'IVA',
        'mascota': 'Mascota',
        'mercado libre': 'Mercado Libre',
    }

    cursor = db.conn.cursor()
    updated = 0

    for key, new_name in corrections.items():
        if isinstance(key, int):
            cursor.execute('UPDATE categoria SET nombre = %s WHERE id_categoria = %s', (new_name, key))
        else:
            cursor.execute('UPDATE categoria SET nombre = %s WHERE nombre = %s', (new_name, key))
        if cursor.rowcount:
            updated += cursor.rowcount

    db.conn.commit()
    print(f'Categorías normalizadas: {updated}')


if __name__ == '__main__':
    clean_category_names()

"""Pruebas unitarias para la grilla de categorías y presupuesto."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.routes.presupuesto import (
    _merge_catalog_categories_into_lines,
    _normalize_lines,
    _period_bounds,
    _infer_tipo_categoria,
    FRECUENCIAS_VALIDAS,
)


class TestPresupuestoGrillaCategorias(unittest.TestCase):
    def test_frecuencias_validas(self):
        self.assertIn('mensualmente', FRECUENCIAS_VALIDAS)
        self.assertIn('quincenal', FRECUENCIAS_VALIDAS)
        self.assertIn('semanal', FRECUENCIAS_VALIDAS)
        self.assertIn('anual', FRECUENCIAS_VALIDAS)

    def test_infer_tipo_categoria(self):
        self.assertEqual(_infer_tipo_categoria('Salario', 75), 'ingreso')
        self.assertEqual(_infer_tipo_categoria('Honorarios', None), 'ingreso')
        self.assertEqual(_infer_tipo_categoria('Ventas', None), 'ingreso')
        self.assertEqual(_infer_tipo_categoria('Luz', 13), 'egreso')
        self.assertEqual(_infer_tipo_categoria('Alimentación', None), 'egreso')
        self.assertEqual(_infer_tipo_categoria('Arriendo', 76), 'egreso')

    def test_merge_catalog_categories_into_lines_agrega_faltantes_y_diferencia_ingreso_egreso(self):
        # Líneas ya presupuestadas previamente
        lines = [
            {
                'id_detalle': 10,
                'id_categoria': 1,
                'categoria': 'Alimentación',
                'frecuencia': 'Mensualmente',
                'tipo': 'egreso',
                'tolerancia': 10.0,
                'importe': 300000.0,
                'estimado': 350000.0,
                'real': 200000.0,
                'diferencia': 150000.0,
                'notas': 'Mercado mensual',
            }
        ]

        # Catálogo general de categorías
        catalog = [
            {'id_categoria': 1, 'nombre': 'Alimentación', 'parent_id': None},
            {'id_categoria': 2, 'nombre': 'Servicios Públicos', 'parent_id': None},
            {'id_categoria': 3, 'nombre': 'Transporte', 'parent_id': None},
            {'id_categoria': 4, 'nombre': 'Salario', 'parent_id': 75},
        ]

        # Gastos reales calculados
        reales_gastos = {
            'alimentación': 200000.0,
            'servicios públicos': 85000.0,
            'transporte': 45000.0,
        }
        reales_ingresos = {
            'salario': 2500000.0,
        }

        merged, total_cat, total_pres = _merge_catalog_categories_into_lines(
            lines=lines,
            catalog_categories=catalog,
            reales_gastos=reales_gastos,
            reales_ingresos=reales_ingresos,
            periodo='mensual',
        )

        # Debe contener las 4 categorías del catálogo
        self.assertEqual(len(merged), 4)
        self.assertEqual(total_cat, 4)
        self.assertEqual(total_pres, 1)

        # La categoría de gasto debe mantener sus valores
        alim = next(l for l in merged if l['categoria'] == 'Alimentación')
        self.assertEqual(alim['estimado'], 350000.0)
        self.assertEqual(alim['tipo'], 'egreso')
        self.assertTrue(alim['en_catalogo'])

        # La categoría de ingreso debe inferirse como 'ingreso' y recibir su ingreso real
        salario = next(l for l in merged if l['categoria'] == 'Salario')
        self.assertEqual(salario['tipo'], 'ingreso')
        self.assertEqual(salario['real'], 2500000.0)
        self.assertFalse(salario['es_fijo'])

    def test_normalizacion_de_lineas(self):
        raw_lines = [
            {'categoria': 'Salud', 'frecuencia': 'mensualmente', 'tipo': 'egreso', 'estimado': 120000, 'importe': 100000, 'es_fijo': True},
            {'categoria': 'Mascotas', 'frecuencia': 'quincenal', 'tipo': 'egreso', 'estimado': 50000, 'es_fijo': False},
            {'categoria': 'Salario', 'frecuencia': 'mensualmente', 'estimado': 2000000, 'parent_id': 75},
            {'categoria': '', 'estimado': 0, 'importe': 0},  # Debe descartarse
        ]
        norm = _normalize_lines(raw_lines)
        self.assertEqual(len(norm), 3)
        self.assertEqual(norm[0]['categoria'], 'Salud')
        self.assertEqual(norm[0]['tipo'], 'egreso')
        self.assertTrue(norm[0]['es_fijo'])
        self.assertEqual(norm[1]['categoria'], 'Mascotas')
        self.assertEqual(norm[1]['tipo'], 'egreso')
        self.assertFalse(norm[1]['es_fijo'])
        self.assertEqual(norm[2]['categoria'], 'Salario')
        self.assertEqual(norm[2]['tipo'], 'ingreso')
        self.assertFalse(norm[2]['es_fijo'])

    def test_merge_catalog_sugiere_gasto_fijo_para_servicios(self):
        catalog = [
            {'id_categoria': 86, 'nombre': 'Luz', 'parent_id': 13},
            {'id_categoria': 83, 'nombre': 'Agua', 'parent_id': 13},
            {'id_categoria': 84, 'nombre': 'Gas', 'parent_id': 13},
            {'id_categoria': 85, 'nombre': 'Triple Play', 'parent_id': 13},
            {'id_categoria': 31, 'nombre': 'Salidas a Comer', 'parent_id': None},
            {'id_categoria': 1, 'nombre': 'Salario', 'parent_id': 75},
        ]
        merged, total_cat, total_pres = _merge_catalog_categories_into_lines(
            lines=[],
            catalog_categories=catalog,
            reales_gastos={},
            reales_ingresos={},
            periodo='mensual',
        )
        luz = next(l for l in merged if l['categoria'] == 'Luz')
        agua = next(l for l in merged if l['categoria'] == 'Agua')
        gas = next(l for l in merged if l['categoria'] == 'Gas')
        triple = next(l for l in merged if l['categoria'] == 'Triple Play')
        comer = next(l for l in merged if l['categoria'] == 'Salidas a Comer')
        salario = next(l for l in merged if l['categoria'] == 'Salario')

        self.assertEqual(luz['tipo'], 'egreso')
        self.assertTrue(luz['es_fijo'])
        self.assertEqual(agua['tipo'], 'egreso')
        self.assertTrue(agua['es_fijo'])
        self.assertEqual(gas['tipo'], 'egreso')
        self.assertTrue(gas['es_fijo'])
        self.assertEqual(triple['tipo'], 'egreso')
        self.assertTrue(triple['es_fijo'])
        self.assertEqual(comer['tipo'], 'egreso')
        self.assertFalse(comer['es_fijo'])
        self.assertEqual(salario['tipo'], 'ingreso')
        self.assertFalse(salario['es_fijo'])
        triple = next(l for l in merged if l['categoria'] == 'Triple Play')
        comer = next(l for l in merged if l['categoria'] == 'Salidas a Comer')

        self.assertTrue(luz['es_fijo'])
        self.assertTrue(agua['es_fijo'])
        self.assertTrue(gas['es_fijo'])
        self.assertTrue(triple['es_fijo'])
        self.assertFalse(comer['es_fijo'])


if __name__ == '__main__':
    unittest.main()

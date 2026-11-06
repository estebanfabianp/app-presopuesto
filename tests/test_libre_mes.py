import unittest

from src.business.services.libre_mes import calcular_dinero_libre_mes
from src.routes.presupuesto import _derivar_lineas_desde_anual


class TestLibreMes(unittest.TestCase):
    def test_calculo_basico(self):
        resultado = calcular_dinero_libre_mes(
            ingresos_mensuales=100,
            gastos_fijos_mensuales=30,
            diferidos_mensuales=40,
            prestamos_mensuales=0,
            otros_compromisos=0,
        )

        self.assertAlmostEqual(resultado['dinero_libre_mes'], 30.0)
        self.assertEqual(resultado['estado'], 'positivo')

    def test_calculo_negativo(self):
        resultado = calcular_dinero_libre_mes(
            ingresos_mensuales=100,
            gastos_fijos_mensuales=60,
            diferidos_mensuales=50,
            prestamos_mensuales=10,
        )

        self.assertAlmostEqual(resultado['dinero_libre_mes'], -20.0)
        self.assertEqual(resultado['estado'], 'negativo')

    def test_incluye_gastos_variables(self):
        resultado = calcular_dinero_libre_mes(
            ingresos_mensuales=100, gastos_fijos_mensuales=20,
            gastos_variables_mensuales=15, prestamos_mensuales=15,
        )
        self.assertEqual(resultado['compromiso_total'], 50)
        self.assertEqual(resultado['dinero_libre_mes'], 50)
        self.assertEqual(resultado['gastos_variables_mensuales'], 15)

    def test_derivacion_anual_a_mensual(self):
        annual_lines = [
            {
                'categoria': 'Vivienda',
                'frecuencia': 'Mensualmente',
                'importe': 1200,
                'estimado': 1200,
                'notas': 'Alquiler',
            },
            {
                'categoria': 'Ahorro',
                'frecuencia': 'Mensualmente',
                'importe': 2400,
                'estimado': 2400,
                'notas': 'Meta',
            },
        ]

        resultado = _derivar_lineas_desde_anual(annual_lines)

        self.assertEqual(len(resultado), 2)
        self.assertAlmostEqual(resultado[0]['importe'], 100.0)
        self.assertAlmostEqual(resultado[0]['estimado'], 100.0)
        self.assertEqual(resultado[0]['notas'], 'Alquiler')
        self.assertAlmostEqual(resultado[1]['importe'], 200.0)
        self.assertAlmostEqual(resultado[1]['estimado'], 200.0)


if __name__ == '__main__':
    unittest.main()

import unittest

from app.business import Business  # Ajusta el import según tu estructura

class TestBusiness(unittest.TestCase):
    def setUp(self):
        self.business = Business(name="Test Company", revenue=10000)

    def test_business_name(self):
        self.assertEqual(self.business.name, "Test Company")

    def test_business_revenue(self):
        self.assertEqual(self.business.revenue, 10000)

    def test_update_revenue(self):
        self.business.update_revenue(15000)
        self.assertEqual(self.business.revenue, 15000)

if __name__ == "__main__":
    unittest.main()
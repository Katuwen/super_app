import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.expense_manager import BudgetManager

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TEST_FILE = "test_budget.json"


class TestBudgetManager(unittest.TestCase):
    def setUp(self):
        self.manager = BudgetManager(data_file=TEST_FILE)
        self.manager.data = {
            "balance": 0,
            "transactions": [],
            "categories": ["Еда", "Транспорт", "Жильё", "Развлечения", "Здоровье", "Одежда"],
            "goals": []
        }
        self.manager.save_data()

    def tearDown(self):
        path = os.path.join(DATA_DIR, TEST_FILE)
        if os.path.exists(path):
            os.remove(path)

    def test_add_expense(self):
        result = self.manager.add_transaction(500, "Еда", "expense")
        self.assertTrue(result)
        self.assertEqual(self.manager.get_balance(), -500)

    def test_add_income(self):
        result = self.manager.add_transaction(10000, "Зарплата", "income")
        self.assertTrue(result)
        self.assertEqual(self.manager.get_balance(), 10000)

    def test_add_negative_amount_fails(self):
        result = self.manager.add_transaction(-100, "Еда", "expense")
        self.assertFalse(result)
        self.assertEqual(self.manager.get_balance(), 0)

    def test_add_zero_amount_fails(self):
        result = self.manager.add_transaction(0, "Еда", "expense")
        self.assertFalse(result)

    def test_get_last_10_transactions(self):
        for i in range(15):
            self.manager.add_transaction(100 + i, "Еда")
        last_10 = self.manager.get_last_10_transactions()
        self.assertEqual(len(last_10), 10)

    def test_get_categories(self):
        cats = self.manager.get_categories()
        self.assertIn("Еда", cats)
        self.assertEqual(len(cats), 6)

    def test_add_category(self):
        self.manager.add_category("Образование")
        self.assertIn("Образование", self.manager.get_categories())

    def test_add_duplicate_category(self):
        initial = len(self.manager.get_categories())
        self.manager.add_category("Еда")
        self.assertEqual(len(self.manager.get_categories()), initial)

    def test_expenses_by_category_current_month(self):
        self.manager.add_transaction(500, "Еда")
        self.manager.add_transaction(300, "Транспорт")
        expenses = self.manager.get_expenses_by_category_current_month()
        self.assertIn("Еда", expenses)
        self.assertEqual(expenses["Еда"], 500)
        self.assertEqual(expenses["Транспорт"], 300)

    def test_balance_income_then_expense(self):
        self.manager.add_transaction(1000, "Зарплата", "income")
        self.manager.add_transaction(200, "Еда")
        self.assertEqual(self.manager.get_balance(), 800)

    def test_transactions_limit_100(self):
        for i in range(110):
            self.manager.add_transaction(10, "Еда")
        self.assertEqual(len(self.manager.data["transactions"]), 100)


if __name__ == "__main__":
    unittest.main()

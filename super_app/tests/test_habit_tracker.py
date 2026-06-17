import unittest
import os
import sys
from app.utils.habit_tracker import HabitTracker
from datetime import datetime, timedelta


# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHabitTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = HabitTracker()
        self.tracker.data_file = "test_habits.json"
        self.tracker.data = {"habits": []}
        self.tracker.save_data()

    def tearDown(self):
        if os.path.exists("test_habits.json"):
            os.remove("test_habits.json")

    def test_add_habit(self):
        habit_id = self.tracker.add_habit("Тестовая привычка")
        self.assertEqual(len(self.tracker.data["habits"]), 1)
        self.assertEqual(self.tracker.data["habits"][0]["name"], "Тестовая привычка")
        self.assertEqual(habit_id, 1)

    def test_mark_habit_once_per_day(self):
        habit_id = self.tracker.add_habit("Тест")
        self.tracker.mark_habit(habit_id, "done")
        with self.assertRaises(ValueError):
            self.tracker.mark_habit(habit_id, "done")

    def test_current_streak(self):
        habit_id = self.tracker.add_habit("Серия")
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.tracker.data["habits"][0]["history"][yesterday] = "done"
        self.tracker.data["habits"][0]["history"][today] = "done"
        self.tracker.save_data()
        self.assertEqual(self.tracker.get_current_streak(habit_id), 2)

    def test_best_streak(self):
        habit_id = self.tracker.add_habit("Лучшая серия")
        for i in range(5):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            self.tracker.data["habits"][0]["history"][date] = "done"
        self.tracker.save_data()
        self.assertEqual(self.tracker.get_best_streak(habit_id), 5)


if __name__ == '__main__':
    unittest.main()

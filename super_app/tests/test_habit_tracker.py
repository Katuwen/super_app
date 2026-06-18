import unittest
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.habit_tracker import HabitTracker

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TEST_FILE = "test_habits.json"


class TestHabitTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = HabitTracker()
        self.tracker.data_file = os.path.join(DATA_DIR, TEST_FILE)
        self.tracker.data = {"habits": []}
        self.tracker.save_data()

    def tearDown(self):
        path = os.path.join(DATA_DIR, TEST_FILE)
        if os.path.exists(path):
            os.remove(path)

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

    def test_edit_habit_name(self):
        habit_id = self.tracker.add_habit("Старое имя")
        self.tracker.edit_habit_name(habit_id, "Новое имя")
        self.assertEqual(self.tracker.data["habits"][0]["name"], "Новое имя")

    def test_edit_nonexistent_habit(self):
        with self.assertRaises(ValueError):
            self.tracker.edit_habit_name(999, "Имя")

    def test_delete_habit(self):
        habit_id = self.tracker.add_habit("Удаляемая")
        self.tracker.delete_habit(habit_id)
        self.assertEqual(len(self.tracker.data["habits"]), 0)

    def test_mark_skipped(self):
        habit_id = self.tracker.add_habit("Пропуск")
        today = datetime.now().strftime("%Y-%m-%d")
        self.tracker.mark_habit(habit_id, "skipped")
        status = self.tracker.data["habits"][0]["history"][today]
        self.assertEqual(status, "skipped")

    def test_mark_nonexistent_habit(self):
        with self.assertRaises(ValueError):
            self.tracker.mark_habit(999, "done")

    def test_current_streak_no_history(self):
        habit_id = self.tracker.add_habit("Без истории")
        self.assertEqual(self.tracker.get_current_streak(habit_id), 0)

    def test_current_streak_gap_breaks(self):
        habit_id = self.tracker.add_habit("Серия с пропуском")
        today = datetime.now().strftime("%Y-%m-%d")
        gap_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        self.tracker.data["habits"][0]["history"][today] = "done"
        self.tracker.data["habits"][0]["history"][gap_date] = "done"
        self.tracker.save_data()
        self.assertEqual(self.tracker.get_current_streak(habit_id), 1)

    def test_best_streak_with_skip(self):
        habit_id = self.tracker.add_habit("Серия с пропуском")
        for i in range(3):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            self.tracker.data["habits"][0]["history"][date] = "done"
        skip_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        self.tracker.data["habits"][0]["history"][skip_date] = "skipped"
        self.tracker.save_data()
        self.assertEqual(self.tracker.get_best_streak(habit_id), 3)


if __name__ == '__main__':
    unittest.main()

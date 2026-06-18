import unittest
import os
import sys
import gc
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.schedule_manager import Lesson, Storage, ScheduleEngine

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


class TestLesson(unittest.TestCase):
    def test_lesson_creation(self):
        lesson = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101", "Иванов И.И.")
        self.assertEqual(lesson.name, "Математика")
        self.assertEqual(lesson.day_of_week, 1)
        self.assertEqual(lesson.lesson_type, "lecture")

    def test_lesson_defaults(self):
        lesson = Lesson(None, "Физика", 2, "11:00", "12:30", "practice", "B202")
        self.assertEqual(lesson.teacher, "")


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.db_name = f"test_storage_{uuid.uuid4().hex[:8]}.db"
        self.db_path = os.path.join(DATA_DIR, self.db_name)
        self.storage = Storage.__new__(Storage)
        self.storage.db_path = self.db_path
        self.storage._init_db()

    def tearDown(self):
        gc.collect()
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def test_add_and_get_all(self):
        lesson = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        lesson_id = self.storage.add(lesson)
        self.assertIsNotNone(lesson_id)
        all_lessons = self.storage.get_all()
        self.assertEqual(len(all_lessons), 1)

    def test_update(self):
        lesson = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        lesson_id = self.storage.add(lesson)
        lesson.id = lesson_id
        lesson.name = "Алгебра"
        self.storage.update(lesson)
        updated = self.storage.get_all()
        self.assertEqual(updated[0].name, "Алгебра")

    def test_delete(self):
        lesson = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        lesson_id = self.storage.add(lesson)
        self.storage.delete(lesson_id)
        self.assertEqual(len(self.storage.get_all()), 0)


class TestScheduleEngine(unittest.TestCase):
    def setUp(self):
        self.db_name = f"test_engine_{uuid.uuid4().hex[:8]}.db"
        self.db_path = os.path.join(DATA_DIR, self.db_name)
        self.engine = ScheduleEngine.__new__(ScheduleEngine)
        self.engine.storage = Storage.__new__(Storage)
        self.engine.storage.db_path = self.db_path
        self.engine.storage._init_db()

    def tearDown(self):
        gc.collect()
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def test_add_lesson(self):
        lesson = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        lesson_id = self.engine.add_lesson(lesson)
        self.assertIsNotNone(lesson_id)

    def test_conflict_detection(self):
        l1 = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        self.engine.add_lesson(l1)
        l2 = Lesson(None, "Физика", 1, "10:30", "12:00", "practice", "B202")
        lesson_id = self.engine.add_lesson(l2)
        self.assertIsNotNone(lesson_id)

    def test_conflict_raises_on_overlap(self):
        l1 = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        self.engine.add_lesson(l1)
        l2 = Lesson(None, "Физика", 1, "10:00", "11:00", "practice", "B202")
        with self.assertRaises(ValueError):
            self.engine.add_lesson(l2)

    def test_no_conflict_different_days(self):
        l1 = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        self.engine.add_lesson(l1)
        l2 = Lesson(None, "Физика", 2, "09:00", "10:30", "practice", "B202")
        lesson_id = self.engine.add_lesson(l2)
        self.assertIsNotNone(lesson_id)

    def test_invalid_time_format(self):
        lesson = Lesson(None, "Математика", 1, "25:00", "10:30", "lecture", "A101")
        with self.assertRaises(ValueError):
            self.engine.add_lesson(lesson)

    def test_end_before_start(self):
        lesson = Lesson(None, "Математика", 1, "10:30", "09:00", "lecture", "A101")
        with self.assertRaises(ValueError):
            self.engine.add_lesson(lesson)

    def test_get_lessons_by_day(self):
        l1 = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        l2 = Lesson(None, "Физика", 3, "11:00", "12:30", "practice", "B202")
        self.engine.add_lesson(l1)
        self.engine.add_lesson(l2)
        mon_lessons = self.engine.get_lessons_by_day(1)
        self.assertEqual(len(mon_lessons), 1)
        self.assertEqual(mon_lessons[0].name, "Математика")

    def test_delete_lesson(self):
        lesson = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        lesson_id = self.engine.add_lesson(lesson)
        self.engine.delete_lesson(lesson_id)
        self.assertEqual(len(self.engine.storage.get_all()), 0)

    def test_weekly_load(self):
        l1 = Lesson(None, "Математика", 1, "09:00", "10:30", "lecture", "A101")
        l2 = Lesson(None, "Физика", 1, "11:00", "12:30", "practice", "B202")
        self.engine.add_lesson(l1)
        self.engine.add_lesson(l2)
        load = self.engine.get_weekly_load()
        self.assertIn(1, load)
        self.assertEqual(load[1], 3.0)


if __name__ == "__main__":
    unittest.main()

import unittest
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TEST_MAIN = "test_notes.json"
TEST_EXPORT = "test_export.json"
TEST_SECOND = "test_notes2.json"


class TestNoteManager(unittest.TestCase):
    def setUp(self):
        from app.utils.note_manager import NoteManager
        self.manager = NoteManager()
        self.manager.data_file = os.path.join(DATA_DIR, TEST_MAIN)
        self.manager.data = {"notes": [], "tags": []}
        self.manager.save_data()

    def tearDown(self):
        for f in (TEST_MAIN, TEST_EXPORT, TEST_SECOND):
            path = os.path.join(DATA_DIR, f)
            if os.path.exists(path):
                os.remove(path)

    # --- Базовые CRUD-операции ---

    def test_add_note(self):
        note_id = self.manager.add_note("Заголовок", "Содержание", ["тег1"])
        self.assertEqual(self.manager.get_notes_count(), 1)
        note = self.manager.get_note_by_id(note_id)
        self.assertEqual(note["title"], "Заголовок")
        self.assertEqual(note["content"], "Содержание")
        self.assertIn("тег1", note["tags"])

    def test_add_note_without_tags(self):
        note_id = self.manager.add_note("Без тегов", "текст")
        note = self.manager.get_note_by_id(note_id)
        self.assertEqual(note["tags"], [])

    def test_edit_note(self):
        note_id = self.manager.add_note("Старый", "Старое содержание")
        self.manager.edit_note(note_id, "Новый", "Новое содержание", ["важно"])
        note = self.manager.get_note_by_id(note_id)
        self.assertEqual(note["title"], "Новый")
        self.assertEqual(note["content"], "Новое содержание")
        self.assertIn("важно", note["tags"])

    def test_edit_nonexistent_note(self):
        with self.assertRaises(ValueError):
            self.manager.edit_note(999, "X", "Y")

    def test_delete_note(self):
        note_id = self.manager.add_note("Удалить", "текст")
        self.manager.delete_note(note_id)
        self.assertIsNone(self.manager.get_note_by_id(note_id))
        self.assertEqual(self.manager.get_notes_count(), 0)

    # --- Тестовые данные из таблицы ---

    def test_note_2_long_content_with_numbering(self):
        content = "1. Завершить практику. 2. Повторить ассемблер. 3. Отдохнуть в воскресенье."
        note_id = self.manager.add_note("План на неделю", content, ["важно", "работа"])
        note = self.manager.get_note_by_id(note_id)
        self.assertEqual(note["content"], content)
        self.assertEqual(len(note["tags"]), 2)

    def test_note_3_urgent_tag(self):
        self.manager.add_note(
            "Ошибка в проекте",
            "При компиляции выдаёт undefined reference. Нужно проверить линковку.",
            ["баг", "срочно"]
        )
        results = self.manager.filter_by_tag("срочно")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Ошибка в проекте")

    def test_note_4_cyrillic_tag_with_space(self):
        note_id = self.manager.add_note(
            "Идея для Тишины",
            "Добавить раздел 'дыхательные упражнения'.",
            ["идея", "Тишина"]
        )
        note = self.manager.get_note_by_id(note_id)
        self.assertIn("Тишина", note["tags"])
        results = self.manager.filter_by_tag("Тишина")
        self.assertEqual(len(results), 1)

    def test_note_5_long_title(self):
        long_title = "Заметка с очень длинным названием, которое точно выходит за пределы поля"
        note_id = self.manager.add_note(long_title, "Краткое содержание", ["тест"])
        note = self.manager.get_note_by_id(note_id)
        self.assertEqual(note["title"], long_title)
        self.assertEqual(len(note["title"]), len(long_title))

    def test_note_6_empty_title_and_content(self):
        note_id = self.manager.add_note("", "", [])
        note = self.manager.get_note_by_id(note_id)
        self.assertEqual(note["title"], "")
        self.assertEqual(note["content"], "")
        self.assertEqual(self.manager.get_notes_count(), 1)

    def test_note_7_special_characters(self):
        content = "Символы: !@#$%^&*()_+-={}[]|;:'\",.<>?/"
        note_id = self.manager.add_note("Теги только", content, ["спецсимволы", "123"])
        note = self.manager.get_note_by_id(note_id)
        self.assertEqual(note["content"], content)
        self.assertIn("спецсимволы", note["tags"])
        self.assertIn("123", note["tags"])

    def test_note_8_search_by_content_word(self):
        self.manager.add_note(
            "Заметка для поиска",
            "Проверка поиска по слову 'тестирование'",
            ["поиск"]
        )
        self.manager.add_note("Другая заметка", "Без искомого слова", [])
        results = self.manager.search_notes("тестирование")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Заметка для поиска")

    def test_note_8_search_by_title_partial(self):
        self.manager.add_note("Изучить код 222", "1111", ["работа", "код"])
        results = self.manager.search_notes("код")
        self.assertTrue(len(results) >= 1)
        titles = [r["title"] for r in results]
        self.assertIn("Изучить код 222", titles)

    def test_note_8_search_by_tag(self):
        self.manager.add_note("Заметка", "текст", ["уникальный_тег_xyz"])
        results = self.manager.search_notes("уникальный_тег_xyz")
        self.assertEqual(len(results), 1)

    def test_note_9_delete_flow(self):
        note_id = self.manager.add_note("Удалить позже", "Временная заметка", ["временно"])
        self.assertIsNotNone(self.manager.get_note_by_id(note_id))
        self.assertEqual(self.manager.get_notes_count(), 1)
        self.manager.delete_note(note_id)
        self.assertIsNone(self.manager.get_note_by_id(note_id))
        self.assertEqual(self.manager.get_notes_count(), 0)

    def test_note_10_mixed_language_tags(self):
        note_id = self.manager.add_note(
            "Смешанные теги",
            "английский и русский одновременно",
            ["work", "учеба", "code"]
        )
        note = self.manager.get_note_by_id(note_id)
        self.assertIn("work", note["tags"])
        self.assertIn("учеба", note["tags"])
        self.assertIn("code", note["tags"])
        self.assertEqual(len(note["tags"]), 3)

    # --- Фильтрация по тегам ---

    def test_filter_by_tag(self):
        self.manager.add_note("A", "текст", ["работа"])
        self.manager.add_note("B", "текст", ["учеба"])
        self.manager.add_note("C", "текст", ["работа", "важно"])
        results = self.manager.filter_by_tag("работа")
        self.assertEqual(len(results), 2)

    def test_filter_by_nonexistent_tag(self):
        self.manager.add_note("A", "текст", ["работа"])
        results = self.manager.filter_by_tag("несуществующий")
        self.assertEqual(len(results), 0)

    def test_filter_by_tag_exact_match(self):
        self.manager.add_note("A", "текст", ["код"])
        self.manager.add_note("B", "текст", ["кодинг"])
        results = self.manager.filter_by_tag("код")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "A")

    # --- Поиск ---

    def test_search_notes(self):
        self.manager.add_note("Покупки", "Молоко, хлеб")
        self.manager.add_note("Работа", "Отчёт к пятнице")
        results = self.manager.search_notes("молоко")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Покупки")

    def test_search_case_insensitive(self):
        self.manager.add_note("Тест", "АССЕМБЛЕР")
        results = self.manager.search_notes("ассемблер")
        self.assertEqual(len(results), 1)

    def test_search_empty_query_returns_all(self):
        self.manager.add_note("A", "1")
        self.manager.add_note("B", "2")
        results = self.manager.search_notes("")
        self.assertEqual(len(results), 2)

    # --- Теги ---

    def test_get_all_tags(self):
        self.manager.add_note("A", "текст", ["работа", "важно"])
        self.manager.add_note("B", "текст", ["учеба"])
        tags = self.manager.get_all_tags()
        self.assertIn("работа", tags)
        self.assertIn("учеба", tags)
        self.assertIn("важно", tags)

    def test_duplicate_tags_not_duplicated(self):
        self.manager.add_note("A", "текст", ["работа"])
        self.manager.add_note("B", "текст", ["работа"])
        tags = self.manager.get_all_tags()
        self.assertEqual(tags.count("работа"), 1)

    # --- Экспорт/Импорт ---

    def test_export_import(self):
        self.manager.add_note("Экспорт", "текст", ["тег"])
        export_path = os.path.join(DATA_DIR, TEST_EXPORT)
        self.manager.export_notes(export_path)
        from app.utils.note_manager import NoteManager
        new_manager = NoteManager()
        new_manager.data_file = os.path.join(DATA_DIR, TEST_SECOND)
        new_manager.data = {"notes": [], "tags": []}
        new_manager.import_notes(export_path)
        self.assertEqual(new_manager.get_notes_count(), 1)

    def test_import_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.import_notes(os.path.join(DATA_DIR, "нет_такого_файла.json"))

    def test_import_no_duplicates(self):
        note_id = self.manager.add_note("A", "текст", ["тег"])
        export_path = os.path.join(DATA_DIR, TEST_EXPORT)
        self.manager.export_notes(export_path)
        from app.utils.note_manager import NoteManager
        new_manager = NoteManager()
        new_manager.data_file = os.path.join(DATA_DIR, TEST_SECOND)
        new_manager.data = {"notes": [], "tags": []}
        new_manager.import_notes(export_path)
        self.assertEqual(new_manager.get_notes_count(), 1)

    # --- Временные метки ---

    def test_timestamps_set_on_create(self):
        note_id = self.manager.add_note("Время", "текст")
        note = self.manager.get_note_by_id(note_id)
        self.assertIn("created_at", note)
        self.assertIn("updated_at", note)
        self.assertEqual(note["created_at"], note["updated_at"])

    def test_updated_at_changes_on_edit(self):
        note_id = self.manager.add_note("Время", "текст")
        note = self.manager.get_note_by_id(note_id)
        note["updated_at"] = "2000-01-01 00:00"
        self.manager.save_data()
        self.manager.edit_note(note_id, "Новое", "новое содержание")
        updated = self.manager.get_note_by_id(note_id)["updated_at"]
        self.assertNotEqual(updated, "2000-01-01 00:00")


if __name__ == '__main__':
    unittest.main()

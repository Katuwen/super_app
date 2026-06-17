import json
import os
from datetime import datetime, timedelta
from matplotlib.dates import date2num


class HabitTracker:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(base_dir, "..", "..", "data", "habits_data.json")
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """Загружает данные из JSON или создает пустую структуру"""
        default_data: dict = {"habits": []}
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return default_data
        return default_data

    def save_data(self):
        """Сохраняет текущее состояние в JSON"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    # --- Управление привычками ---

    def add_habit(self, name: str) -> int:
        """Создает новую привычку и возвращает её ID"""
        habit_id = len(self.data["habits"]) + 1
        habit = {
            "id": habit_id,
            "name": name,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "history": {}
        }
        self.data["habits"].append(habit)
        self.save_data()
        return habit_id

    def edit_habit_name(self, habit_id: int, new_name: str):
        """Редактирует название привычки"""
        for habit in self.data["habits"]:
            if habit["id"] == habit_id:
                habit["name"] = new_name
                self.save_data()
                return
        raise ValueError("Привычка не найдена")

    def delete_habit(self, habit_id: int):
        """Удаляет привычку по ID"""
        self.data["habits"] = [
            h for h in self.data["habits"]
            if h["id"] != habit_id
        ]
        self.save_data()

    # --- Ежедневная отметка ---

    def mark_habit(self, habit_id: int, status: str = "done"):
        """
        Отмечает привычку как выполненную ('done') или пропущенную ('skipped')
        Запрещает повторную отметку в тот же день
        """
        today = datetime.now().strftime("%Y-%m-%d")
        for habit in self.data["habits"]:
            if habit["id"] == habit_id:
                if today in habit["history"]:
                    raise ValueError("Вы уже отметили эту привычку сегодня!")
                habit["history"][today] = status
                self.save_data()
                return
        raise ValueError("Привычка не найдена")

    # --- Расчет серий ---

    def get_current_streak(self, habit_id: int) -> int:
        """Возвращает текущую серию дней подряд без пропусков"""
        for habit in self.data["habits"]:
            if habit["id"] == habit_id:
                history = habit["history"]
                if not history:
                    return 0
                # Сортируем даты по убыванию
                sorted_dates = sorted(history.keys(), reverse=True)
                today = datetime.now().strftime("%Y-%m-%d")
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                latest = sorted_dates[0]
                if latest != today and latest != yesterday:
                    return 0
                streak = 0
                expected_date = datetime.strptime(latest, "%Y-%m-%d")
                for date_str in sorted_dates:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    # Проверяем, что дата идет подряд
                    if date_obj == expected_date or date_obj == expected_date - timedelta(days=1):
                        if history[date_str] == "done":
                            streak += 1
                            expected_date = date_obj - timedelta(days=1)
                        else:
                            break  # Пропуск прерывает серию
                    else:
                        break  # Разрыв в датах
                return streak
        return 0

    def get_best_streak(self, habit_id: int) -> int:
        """Возвращает лучшую серию за все время"""
        for habit in self.data["habits"]:
            if habit["id"] == habit_id:
                history = habit["history"]
                if not history:
                    return 0
                sorted_dates = sorted(history.keys())
                best_streak = 0
                current_streak = 0
                prev_date = None
                for date_str in sorted_dates:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if history[date_str] != "done":
                        current_streak = 0
                        prev_date = None
                        continue
                    if prev_date is None or (date_obj - prev_date).days == 1:
                        current_streak += 1
                    else:
                        current_streak = 1
                    best_streak = max(best_streak, current_streak)
                    prev_date = date_obj
                return best_streak
        return 0

    # --- Экспорт/Импорт ---

    def export_data(self, filename: str = "habits_export.json"):
        """Экспортирует данные в указанный файл"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        export_path = os.path.join(base_dir, "..", "..", "data", filename)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def import_data(self, filename: str):
        """Импортирует данные из указанного файла"""
        if not os.path.exists(filename):
            raise FileNotFoundError("Файл импорта не найден")
        with open(filename, 'r', encoding='utf-8') as f:
            imported_data = json.load(f)
        self.data = imported_data
        self.save_data()

    # --- Визуализация (простой график серий) ---

    def plot_habit_progress(self, habit_id: int):
        """Строит график выполнения привычки по дням"""
        import matplotlib.pyplot as plt
        from matplotlib.dates import DateFormatter
        for habit in self.data["habits"]:
            if habit["id"] == habit_id:
                history = habit["history"]
                if not history:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.text(
                        0.5, 0.5, 'Нет данных для отображения',
                        ha='center', va='center', transform=ax.transAxes
                    )
                    return fig
                dates = []
                values = []
                for date_str, status in sorted(history.items()):
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    dates.append(date_obj)
                    values.append(1 if status == "done" else 0)
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.bar(date2num(dates), values, color=['#2ecc71' if v == 1 else '#e74c3c' for v in values])
                ax.set_title(f'Прогресс привычки: {habit["name"]}')
                ax.set_ylabel('Выполнено (1) / Пропущено (0)')
                ax.xaxis.set_major_formatter(DateFormatter('%d.%m'))
                plt.xticks(rotation=45)
                plt.tight_layout()
                return fig
        raise ValueError("Привычка не найдена")

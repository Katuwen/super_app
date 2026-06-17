import os
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

# --- Модель занятия ---


@dataclass
class Lesson:
    id: Optional[int]
    name: str
    day_of_week: int  # 1=Пн, 7=Вс
    start_time: str   # "09:00"
    end_time: str     # "10:30"
    lesson_type: str  # lecture/practice/lab/seminar
    room: str
    teacher: str = ""

# --- Хранилище ---


class Storage:
    def __init__(self, db_path: str = "schedule.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, "..", "..", "data", db_path)
        self._init_db()

    def _init_db(self):
        """Создает таблицу, если её нет"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    day_of_week INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    lesson_type TEXT NOT NULL,
                    room TEXT NOT NULL,
                    teacher TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_lessons_day
                ON lessons(day_of_week, start_time)
            """)
            conn.commit()

    def get_all(self) -> List[Lesson]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM lessons ORDER BY day_of_week, start_time")
            return [Lesson(*row) for row in cursor.fetchall()]

    def add(self, lesson: Lesson) -> Optional[int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO lessons (name, day_of_week, start_time, end_time, lesson_type, room, teacher)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (lesson.name, lesson.day_of_week, lesson.start_time,
                 lesson.end_time, lesson.lesson_type, lesson.room, lesson.teacher)
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, lesson: Lesson):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE lessons SET name=?, day_of_week=?, start_time=?, end_time=?,
                lesson_type=?, room=?, teacher=? WHERE id=?
            """, (lesson.name, lesson.day_of_week, lesson.start_time,
                  lesson.end_time, lesson.lesson_type, lesson.room, lesson.teacher, lesson.id))
            conn.commit()

    def delete(self, lesson_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
            conn.commit()

# --- Движок расписания ---


class ScheduleEngine:
    DAYS_RU = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 7: "Вс"}
    TYPES_RU = {
        "lecture": "Лекция", "practice": "Практика",
        "lab": "Лаб. работа", "seminar": "Семинар"
    }

    def __init__(self):
        self.storage = Storage()

    def add_lesson(self, lesson: Lesson) -> Optional[int]:
        """Добавляет занятие с валидацией"""
        self._validate_times(lesson.start_time, lesson.end_time)
        self._check_conflicts(lesson)
        return self.storage.add(lesson)

    def update_lesson(self, lesson: Lesson):
        self._validate_times(lesson.start_time, lesson.end_time)
        self._check_conflicts(lesson, exclude_id=lesson.id)
        self.storage.update(lesson)

    def delete_lesson(self, lesson_id: int):
        self.storage.delete(lesson_id)

    def get_lessons_by_day(self, day: int) -> List[Lesson]:
        return [lesson for lesson in self.storage.get_all() if lesson.day_of_week == day]

    def get_today_lessons(self) -> List[Lesson]:
        # isoweekday(): 1=Пн, 7=Вс
        return self.get_lessons_by_day(datetime.now().isoweekday())

    def get_next_lesson(self) -> Optional[Lesson]:
        """Возвращает следующее занятие от текущего момента"""
        now = datetime.now()
        today = now.isoweekday()
        current_time = now.strftime("%H:%M")

        # Ищем сегодняшние занятия после текущего времени
        for lesson in self.get_lessons_by_day(today):
            if lesson.start_time >= current_time:
                return lesson

        # Если сегодня больше нет — ищем завтра и дальше
        for day_offset in range(1, 8):
            next_day = ((today - 1 + day_offset) % 7) + 1
            day_lessons = self.get_lessons_by_day(next_day)
            if day_lessons:
                return day_lessons[0]  # Первое занятие дня

        return None

    def get_time_until_next(self) -> Optional[str]:
        """Возвращает строку обратного отсчета до следующей пары"""
        next_lesson = self.get_next_lesson()
        if not next_lesson:
            return "Нет предстоящих занятий"

        now = datetime.now()
        target_day = next_lesson.day_of_week
        today = now.isoweekday()

        # Вычисляем дату следующего занятия
        days_ahead = (target_day - today) % 7

        target_date = now + timedelta(days=days_ahead)
        target_datetime = datetime.strptime(
            f"{target_date.strftime('%Y-%m-%d')} {next_lesson.start_time}",
            "%Y-%m-%d %H:%M"
        )

        delta = target_datetime - now
        if delta.total_seconds() <= 0:
            return "Занятие начинается сейчас!"

        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes = remainder // 60
        seconds = remainder % 60

        return f"{next_lesson.name} через {hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_weekly_load(self) -> dict:
        """Возвращает количество часов по дням недели для графика"""
        lessons = self.storage.get_all()
        load = {i: 0.0 for i in range(1, 8)}

        for lesson in lessons:
            start = datetime.strptime(lesson.start_time, "%H:%M")
            end = datetime.strptime(lesson.end_time, "%H:%M")
            duration = (end - start).total_seconds() / 3600
            load[lesson.day_of_week] += duration

        return load

    # --- Валидация ---

    def _validate_times(self, start: str, end: str):
        """Проверяет корректность времени"""
        try:
            s = datetime.strptime(start, "%H:%M")
            e = datetime.strptime(end, "%H:%M")
        except ValueError:
            raise ValueError("Некорректный формат времени (используйте ЧЧ:ММ)")

        if e <= s:
            raise ValueError("Время окончания должно быть позже времени начала")

    def _check_conflicts(self, lesson: Lesson, exclude_id: Optional[int] = None):
        """Проверяет пересечение с другими занятиями в тот же день"""
        for existing in self.get_lessons_by_day(lesson.day_of_week):
            if exclude_id is not None and existing.id == exclude_id:
                continue

            # Проверяем пересечение интервалов
            if not (lesson.end_time <= existing.start_time or
                    lesson.start_time >= existing.end_time):
                raise ValueError(
                    f"Конфликт с занятием '{existing.name}' "
                    f"({existing.start_time}-{existing.end_time})"
                )

    def plot_weekly_load(self):
        """Строит столбчатую диаграмму нагрузки по дням"""
        import matplotlib.pyplot as plt

        load = self.get_weekly_load()
        days = [self.DAYS_RU[i] for i in range(1, 8)]
        hours = [load[i] for i in range(1, 8)]

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ['#3498db' if h > 0 else '#95a5a6' for h in hours]
        ax.bar(days, hours, color=colors)

        ax.set_title("Учебная нагрузка по дням недели (часы)")
        ax.set_ylabel("Часов занятий")
        ax.set_ylim(0, max(hours) + 2 if max(hours) > 0 else 10)
        ax.grid(axis='y', alpha=0.3)

        # Подписи значений на столбцах
        for i, v in enumerate(hours):
            if v > 0:
                ax.text(i, v + 0.1, f"{v:.1f}ч", ha='center', fontsize=10)

        plt.tight_layout()
        return fig

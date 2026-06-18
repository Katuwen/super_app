# SuperApp v2.0

Мульти-утилитное десктопное приложение на Python с графическим интерфейсом.

## Выбор UI-фреймворка

**CustomTkinter** — надстройка над стандартным tkinter.

Причины выбора:
- Современный дизайн "из коробки" (тёмная тема, скруглённые углы)
- Нативность и лёгкость — не требует дополнительных сред выполнения
- Простая интеграция графиков matplotlib
- Масштабируемость — каждый модуль в отдельном файле

## Установка и запуск

```bash
pip install -r requirements.txt
python main.py
```

## Модули

### 💱 Курс Валют (Currency Tracker)
Файл: `app/utils/currency_tracker.py`

Получение текущих курсов валют ЦБ РФ и отображение динамики за последние 7 дней.

### 💰 Расходы (Budget & Goals)
Файл: `app/utils/expense_manager.py`

Учёт доходов и расходов с балансом, категориями и круговой диаграммой.

### ✅ Привычки (Habit Tracker)
Файл: `app/utils/habit_tracker.py`

Отслеживание ежедневных привычек с расчётом серий выполнения и графиком прогресса.

### 📅 Расписание (Schedule Manager)
Файл: `app/utils/schedule_manager.py`

Управление учебным расписанием с таймером обратного отсчёта и визуализацией нагрузки.

### 📝 Блокнот (Quick Notes)
Файл: `app/utils/note_manager.py`

Менеджер заметок с тегами, поиском и фильтрацией.

- Создание, редактирование и удаление заметок
- Поиск по содержимому и заголовку
- Фильтрация по тегам
- Экспорт/импорт данных

## Тесты

71 юнит-тест покрывающий все 5 утилит.

```bash
# Запуск всех тестов
python -m unittest discover -s tests -v

# Запуск конкретного модуля
python tests/test_currency_tracker.py
```

### Покрытие по модулям

| Модуль | Тестов | Файл |
|--------|--------|------|
| Currency Tracker | 5 | `test_currency_tracker.py` |
| Expense Manager | 11 | `test_expense_manager.py` |
| Habit Tracker | 12 | `test_habit_tracker.py` |
| Note Manager | 29 | `test_note_manager.py` |
| Schedule Manager | 14 | `test_schedule_manager.py` |
| **Итого** | **71** | |

## Структура проекта

```
super_app/
├── main.py                        # Точка входа
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Конфигурация приложения
│   │   └── navigation.py          # Навигация между модулями
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── views.py               # Главное окно и виджеты
│   │   └── styles.py              # Цвета, шрифты, размеры
│   └── utils/
│       ├── __init__.py
│       ├── currency_tracker.py    # Курсы валют ЦБ РФ
│       ├── expense_manager.py     # Учёт доходов/расходов
│       ├── habit_tracker.py       # Трекер привычек
│       ├── note_manager.py        # Блокнот заметок
│       └── schedule_manager.py    # Учебное расписание
├── data/                          # Файлы данных (JSON, SQLite)
│   ├── budget_data.json
│   ├── habits_data.json
│   ├── notes_data.json
│   └── schedule.db
├── tests/
│   ├── test_currency_tracker.py   # Тесты модуля валют (5)
│   ├── test_expense_manager.py    # Тесты модуля расходов (11)
│   ├── test_habit_tracker.py      # Тесты модуля привычек (12)
│   ├── test_note_manager.py       # Тесты модуля заметок (29)
│   └── test_schedule_manager.py   # Тесты модуля расписания (14)
├── .gitignore                     # Игнорирование venv, кэша, БД
├── mypy.ini                       # Конфигурация mypy
├── requirements.txt               # Зависимости проекта
└── README.md
```

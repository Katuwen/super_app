# SuperApp v1.0

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

```bash
python -m unittest discover tests -v
```

## Структура проекта

```
super_app/
├── main.py                    # Точка входа
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── navigation.py
│   ├── ui/
│   │   ├── views.py           # Главное окно и виджеты
│   │   └── styles.py          # Цвета, шрифты, размеры
│   └── utils/
│       ├── currency_tracker.py
│       ├── expense_manager.py
│       ├── habit_tracker.py
│       ├── schedule_manager.py
│       └── note_manager.py
├── tests/
│   ├── test_habit_tracker.py
│   └── test_note_manager.py
├── requirements.txt
└── README.md
```

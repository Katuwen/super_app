# Окна и виджеты (Главное окно + окна утилит)

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.utils.currency_tracker import CurrencyTracker, plot_currency_dynamics
from app.utils.expense_manager import BudgetManager
from datetime import datetime
from app.utils.habit_tracker import HabitTracker
from app.utils.schedule_manager import ScheduleEngine, Lesson
from app.ui.styles import *


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SuperApp v1.0")
        self.geometry(WIDTH_WINDOW)
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self._timer_id = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- БОКОВАЯ ПАНЕЛЬ ---
        self.sidebar_frame = ctk.CTkFrame(self, width=WIDTH_SIDEBAR, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="SUPER APP",
            font=FONT_LOGO, text_color=COLOR_PRIMARY
        )
        self.logo_label.grid(row=0, column=0, padx=PAD_SIDEBAR, pady=(30, 0))

        self.btn_currency = ctk.CTkButton(
            self.sidebar_frame,
            text="💱 Курс Валют",
            command=self.show_currency_view,
            height=BTN_SIDEBAR_HEIGHT
        )
        self.btn_currency.grid(row=1, column=0, padx=PAD_SIDEBAR, pady=10, sticky="ew")

        self.btn_expenses = ctk.CTkButton(
            self.sidebar_frame,
            text="💰 Расходы",
            command=self.show_expense_view,
            height=BTN_SIDEBAR_HEIGHT
        )
        self.btn_expenses.grid(row=2, column=0, padx=PAD_SIDEBAR, pady=10, sticky="ew")

        self.btn_crypto = ctk.CTkButton(
            self.sidebar_frame, text="🪙 Крипто (Скоро)", state="disabled",
            fg_color=COLOR_DISABLED_BG, height=BTN_SIDEBAR_HEIGHT
        )
        self.btn_crypto.grid(row=3, column=0, padx=PAD_SIDEBAR, pady=10, sticky="ew")

        self.btn_habits = ctk.CTkButton(
            self.sidebar_frame,
            text="✅ Привычки",
            command=self.show_habit_view,
            height=BTN_SIDEBAR_HEIGHT
        )
        self.btn_habits.grid(row=4, column=0, padx=PAD_SIDEBAR, pady=10, sticky="ew")

        self.btn_schedule = ctk.CTkButton(
            self.sidebar_frame,
            text=" Расписание",
            command=self.show_schedule_view,
            height=BTN_SIDEBAR_HEIGHT
        )
        self.btn_schedule.grid(row=5, column=0, padx=PAD_SIDEBAR, pady=10, sticky="ew")

        # --- ОБЛАСТЬ КОНТЕНТА ---
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLOR_CONTENT_BG
        )
        self.content_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=PAD_CONTENT,
            pady=PAD_CONTENT
        )

        self.show_currency_view()

    def clear_content(self):
        self._cancel_timer()
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _cancel_timer(self):
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None

    def show_currency_view(self):
        self.clear_content()
        container = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CONTENT_BG)
        container.pack(fill="both", expand=True)

        title = ctk.CTkLabel(
            container,
            text="Динамика курса валют (ЦБ РФ)",
            font=FONT_TITLE
        )
        title.pack(pady=10)

        try:
            tracker = CurrencyTracker()
            df = tracker.get_current_rates()
            if df is not None and not df.empty:
                target = df[df['CharCode'] == 'USD']
                if not target.empty:
                    current_rate = target.iloc[0]['ValCurs']
                    curr_name = target.iloc[0]['Name']

                    info_label = ctk.CTkLabel(
                        container,
                        text=(
                            f"Текущий курс {curr_name}: "
                            f"{current_rate:.2f} RUB"
                        ),
                        font=FONT_BODY, text_color=COLOR_SUCCESS
                    )
                    info_label.pack(pady=5)

                    fig = plot_currency_dynamics("USD", days=7)
                    canvas = FigureCanvasTkAgg(fig, master=container)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill="both", expand=True)
                else:
                    ctk.CTkLabel(
                        container,
                        text="⚠️ USD не найден в ответе ЦБ.",
                        text_color=COLOR_WARNING).pack(pady=20)
            else:
                ctk.CTkLabel(container,
                             text="⚠️ Не удалось загрузить данные ЦБ.",
                             font=FONT_BODY).pack(pady=20)
        except Exception as e:
            ctk.CTkLabel(container,
                         text=f"Ошибка: {e}",
                         text_color=COLOR_DANGER).pack(pady=20)

    def show_expense_view(self):
        self.clear_content()
        container = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CONTENT_BG)
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container,
                     text="Учёт расходов",
                     font=FONT_TITLE).pack(pady=(0, 15))

        try:
            manager = BudgetManager()
            balance = manager.get_balance()

            # Баланс
            bal_frame = ctk.CTkFrame(
                container,
                fg_color=(COLOR_CARD_BG_LIGHT, COLOR_CARD_BG_DARK)
            )
            bal_frame.pack(pady=10, padx=20, fill="x")
            ctk.CTkLabel(bal_frame,
                         text="Текущий баланс:",
                         font=FONT_SMALL).pack(side="left", padx=10)
            bal_color = COLOR_SUCCESS if balance >= 0 else COLOR_DANGER
            ctk.CTkLabel(bal_frame,
                         text=f"{balance:,.2f} ₽",
                         font=FONT_SMALL_BOLD,
                         text_color=bal_color).pack(
                side="right", padx=10)

            # Форма ввода
            form = ctk.CTkFrame(container, fg_color=COLOR_CONTENT_BG)
            form.pack(fill="x", padx=20, pady=10)

            ctk.CTkLabel(form,
                         text="Сумма:").grid(row=0,
                                             column=0,
                                             padx=5,
                                             sticky="w")
            entry_amount = ctk.CTkEntry(form,
                                        width=100,
                                        placeholder_text="0.00")
            entry_amount.grid(row=0, column=1, padx=5)

            ctk.CTkLabel(form,
                         text="Категория:").grid(row=0,
                                                 column=2,
                                                 padx=5,
                                                 sticky="w")
            combo_cat = ctk.CTkComboBox(form,
                                        values=manager.get_categories(),
                                        width=120)
            combo_cat.set(manager.get_categories()[0])
            combo_cat.grid(row=0, column=3, padx=5)

            ctk.CTkLabel(form,
                         text="Тип:").grid(row=0,
                                           column=4,
                                           padx=5,
                                           sticky="w")
            seg_type = ctk.CTkSegmentedButton(form,
                                              values=["Расход",
                                                      "Доход"], width=100)
            seg_type.set("Расход")
            seg_type.grid(row=0, column=5, padx=5)

            def on_add():
                try:
                    amount = float(entry_amount.get())
                    category = combo_cat.get()
                    trans_type = (
                        "expense"
                        if seg_type.get() == "Расход"
                        else "income"
                    )
                    if manager.add_transaction(amount, category, trans_type):
                        entry_amount.delete(0, 'end')
                        self.show_expense_view()  # Обновляем экран
                    else:
                        ctk.CTkLabel(container,
                                     text="⚠️ Введите сумму > 0",
                                     text_color=COLOR_WARNING).pack(pady=5)
                except ValueError:
                    ctk.CTkLabel(container,
                                 text="⚠️ Ошибка формата числа",
                                 text_color=COLOR_DANGER).pack(pady=5)

            ctk.CTkButton(form,
                          text="➕ Добавить",
                          command=on_add,
                          width=BTN_ACTION_WIDTH,
                          height=BTN_HEIGHT).grid(row=0,
                                          column=6,
                                          padx=10)

            # Нижняя часть: История + График
            bottom = ctk.CTkFrame(container, fg_color=COLOR_CONTENT_BG)
            bottom.pack(fill="both", expand=True, pady=10)

            # Список транзакций
            list_frame = ctk.CTkFrame(bottom, fg_color=COLOR_CARD_BG)
            list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            ctk.CTkLabel(list_frame,
                         text="Последние операции",
                         font=FONT_SUBTITLE).pack(pady=5)

            scroll_trans = ctk.CTkScrollableFrame(list_frame, height=250)
            scroll_trans.pack(fill="both", expand=True, padx=5, pady=5)

            for t in manager.get_last_10_transactions():
                sign = "+" if t["type"] == "income" else "-"
                color = COLOR_SUCCESS if t["type"] == "income" else COLOR_DANGER
                row = ctk.CTkFrame(scroll_trans, fg_color=COLOR_CONTENT_BG)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row,
                             text=t["date"],
                             width=90, anchor="w").pack(side="left")
                ctk.CTkLabel(row,
                             text=t["category"],
                             width=100, anchor="w").pack(side="left")
                ctk.CTkLabel(row,
                             text=f"{sign}{t['amount']:.2f} ₽",
                             text_color=color,
                             font=FONT_SMALL_BOLD).pack(side="right")

            # График
            chart_frame = ctk.CTkFrame(bottom, fg_color=COLOR_CARD_BG)
            chart_frame.pack(side="right",
                             fill="both",
                             expand=True,
                             padx=(5, 0))
            ctk.CTkLabel(chart_frame,
                         text="Диаграмма расходов",
                         font=FONT_SUBTITLE).pack(pady=5)

            fig = manager.plot_expenses_pie()
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            ctk.CTkLabel(container,
                         text=f"Ошибка инициализации модуля: {e}",
                         text_color=COLOR_DANGER).pack(pady=20)

    def show_habit_view(self):
        self.clear_content()
        container = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CONTENT_BG)
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container, text="Трекер привычек", font=FONT_TITLE).pack(pady=10)

        tracker = HabitTracker()

        # Панель добавления
        add_frame = ctk.CTkFrame(container)
        add_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(add_frame, text="Название:").pack(side="left", padx=5)
        entry_name = ctk.CTkEntry(add_frame, width=200)
        entry_name.pack(side="left", padx=5)

        def add_habit():
            name = entry_name.get().strip()
            if name:
                tracker.add_habit(name)
                entry_name.delete(0, 'end')
                self.show_habit_view()
            else:
                ctk.CTkLabel(container, text="Введите название", text_color=COLOR_WARNING).pack(pady=2)

        ctk.CTkButton(add_frame, text="➕ Добавить", command=add_habit,
                      width=BTN_ACTION_WIDTH, height=BTN_HEIGHT).pack(side="left", padx=5)

        # Список привычек
        list_frame = ctk.CTkScrollableFrame(container, height=200)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        if not tracker.data["habits"]:
            ctk.CTkLabel(list_frame, text="Нет привычек. Добавьте первую!").pack(pady=10)
        else:
            for habit in tracker.data["habits"]:
                habit_frame = ctk.CTkFrame(list_frame)
                habit_frame.pack(fill="x", pady=2)

                ctk.CTkLabel(habit_frame, text=habit["name"], width=150, anchor="w").pack(side="left", padx=5)

                today = datetime.now().strftime("%Y-%m-%d")
                already_done = today in habit["history"]
                btn_mark = ctk.CTkButton(
                    habit_frame,
                    text="✅" if not already_done else "✔️ Выполнено",
                    width=BTN_ACTION_WIDTH,
                    height=BTN_HEIGHT,
                    state="normal" if not already_done else "disabled",
                    command=lambda hid=habit["id"]: self._mark_habit_and_refresh(hid, tracker)
                )
                btn_mark.pack(side="left", padx=5)

                streak = tracker.get_current_streak(habit["id"])
                ctk.CTkLabel(habit_frame, text=f"🔥 {streak} дн.").pack(side="left", padx=5)

                ctk.CTkButton(
                    habit_frame,
                    text="🗑️",
                    width=BTN_ICON_WIDTH,
                    height=BTN_HEIGHT,
                    fg_color=COLOR_DANGER,
                    hover_color=COLOR_DANGER_HOVER,
                    command=lambda hid=habit["id"]: self._delete_habit_and_refresh(hid, tracker)
                ).pack(side="right", padx=5)

        # График первой привычки
        if tracker.data["habits"]:
            try:
                first_id = tracker.data["habits"][0]["id"]
                fig = tracker.plot_habit_progress(first_id)
                canvas = FigureCanvasTkAgg(fig, master=container)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
            except Exception as e:
                ctk.CTkLabel(container, text=f"График не загружен: {e}", text_color=COLOR_DANGER).pack()

    def _mark_habit_and_refresh(self, habit_id: int, tracker):
        try:
            tracker.mark_habit(habit_id, "done")
            self.show_habit_view()
        except ValueError as e:
            ctk.CTkLabel(self.content_frame, text=str(e), text_color=COLOR_DANGER).pack(pady=5)

    def _delete_habit_and_refresh(self, habit_id: int, tracker):
        tracker.delete_habit(habit_id)
        self.show_habit_view()

    def show_placeholder(self, name):
        self.clear_content()
        label = ctk.CTkLabel(self.content_frame,
                             text=f"Модуль '{name}' в разработке...",
                             font=FONT_TITLE)
        label.pack(expand=True)

    def show_schedule_view(self):
        """Отображает расписание с сеткой недели и таймером"""
        self.clear_content()
        engine = ScheduleEngine()
        # Заголовок и таймер
        header_frame = ctk.CTkFrame(self.content_frame)
        header_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(
            header_frame,
            text="📅 Расписание занятий",
            font=FONT_TITLE
        ).pack(pady=5)
        # Таймер обратного отсчета
        self.timer_label = ctk.CTkLabel(
            header_frame,
            text=engine.get_time_until_next(),
            font=FONT_COUNTDOWN,
            text_color=COLOR_SUCCESS
        )
        self.timer_label.pack(pady=5)
        # Кнопка добавления
        ctk.CTkButton(
            header_frame,
            text="+ Добавить занятие",
            command=lambda: self._add_lesson_dialog(engine),
            width=BTN_ACTION_WIDTH,
            height=BTN_HEIGHT
        ).pack(pady=5)
        #   Сетка недели (7 дней)
        days_frame = ctk.CTkScrollableFrame(self.content_frame)
        days_frame.pack(fill="both", expand=True)
        for day_num in range(1, 8):
            day_name = engine.DAYS_RU[day_num]
            lessons = engine.get_lessons_by_day(day_num)
            day_frame = ctk.CTkFrame(days_frame)
            day_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(
                day_frame,
                text=f"{day_name} ({len(lessons)} зан.)",
                font=FONT_SUBTITLE,
                width=100
            ).pack(side="left", padx=10)
            # Список занятий дня
            lessons_frame = ctk.CTkFrame(day_frame, fg_color=COLOR_CONTENT_BG)
            lessons_frame.pack(side="left", expand=True, fill="x")
            if not lessons:
                ctk.CTkLabel(lessons_frame, text="—", text_color=COLOR_TEXT_MUTED).pack(side="left")
            else:
                for lesson in lessons:
                    lesson_text = (
                        f"{lesson.start_time}-{lesson.end_time} | "
                        f"{lesson.name} | {lesson.room}"
                    )
                    ctk.CTkLabel(lessons_frame, text=lesson_text).pack(side="left", padx=5)
            # Кнопка удаления (для последнего занятия)
            if lessons:
                ctk.CTkButton(
                    day_frame,
                    text="✕",
                    width=BTN_ICON_WIDTH,
                    height=BTN_HEIGHT,
                    fg_color=COLOR_DANGER,
                    hover_color=COLOR_DANGER_HOVER,
                    command=lambda lid=lessons[-1].id: self._delete_lesson(engine, lid)
                ).pack(side="right", padx=10)

        fig = engine.plot_weekly_load()
        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
        # Запускаем обновление таймера каждую секунду
        self._update_timer(engine)

    def _update_timer(self, engine):
        """Обновляет таймер каждую секунду (аналог QTimer)"""
        try:
            self.timer_label.configure(text=engine.get_time_until_next())
        except Exception:
            return
        self._timer_id = self.after(1000, lambda: self._update_timer(engine))

    def _add_lesson_dialog(self, engine: ScheduleEngine):
        """Создаёт окно для добавления нового занятия"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Добавление занятия")
        dialog.geometry("400x500")
        dialog.grab_set()  # модальное окно

        # Поля ввода
        ctk.CTkLabel(dialog, text="Название занятия:").pack(pady=(10, 0))
        entry_name = ctk.CTkEntry(dialog, width=300)
        entry_name.pack(pady=5)

        ctk.CTkLabel(dialog, text="День недели (1-Пн ... 7-Вс):").pack(pady=(10, 0))
        combo_day = ctk.CTkComboBox(
            dialog,
            values=[f"{i} - {engine.DAYS_RU[i]}" for i in range(1, 8)],
            width=300
        )
        combo_day.set("1 - Пн")
        combo_day.pack(pady=5)

        ctk.CTkLabel(dialog, text="Время начала (ЧЧ:ММ):").pack(pady=(10, 0))
        entry_start = ctk.CTkEntry(dialog, width=300, placeholder_text="09:00")
        entry_start.pack(pady=5)

        ctk.CTkLabel(dialog, text="Время окончания (ЧЧ:ММ):").pack(pady=(10, 0))
        entry_end = ctk.CTkEntry(dialog, width=300, placeholder_text="10:30")
        entry_end.pack(pady=5)

        ctk.CTkLabel(dialog, text="Тип занятия:").pack(pady=(10, 0))
        combo_type = ctk.CTkComboBox(
            dialog,
            values=["lecture", "practice", "lab", "seminar"],
            width=300
        )
        combo_type.set("lecture")
        combo_type.pack(pady=5)

        ctk.CTkLabel(dialog, text="Аудитория:").pack(pady=(10, 0))
        entry_room = ctk.CTkEntry(dialog, width=300, placeholder_text="101")
        entry_room.pack(pady=5)

        ctk.CTkLabel(dialog, text="Преподаватель (опционально):").pack(pady=(10, 0))
        entry_teacher = ctk.CTkEntry(dialog, width=300, placeholder_text="Иванов И.И.")
        entry_teacher.pack(pady=5)

        # Функция сохранения
        def on_save():
            try:
                # Парсим день недели
                day_str = combo_day.get().split()[0]
                day = int(day_str)
                name = entry_name.get().strip()
                start = entry_start.get().strip()
                end = entry_end.get().strip()
                lesson_type = combo_type.get()
                room = entry_room.get().strip()
                teacher = entry_teacher.get().strip()

                if not name or not start or not end or not room:
                    ctk.CTkLabel(dialog, text="Заполните все обязательные поля!", text_color=COLOR_DANGER).pack()
                    return

                lesson = Lesson(
                    id=None,
                    name=name,
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    lesson_type=lesson_type,
                    room=room,
                    teacher=teacher
                )
                engine.add_lesson(lesson)
                dialog.destroy()
                self.show_schedule_view()  # обновить расписание
            except Exception as e:
                # Показать ошибку в диалоге
                error_label = ctk.CTkLabel(dialog, text=f"Ошибка: {e}", text_color=COLOR_DANGER)
                error_label.pack(pady=5)

        # Кнопки
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Сохранить", command=on_save,
                      width=BTN_ACTION_WIDTH, height=BTN_HEIGHT).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Отмена", command=dialog.destroy,
                      width=BTN_ACTION_WIDTH, height=BTN_HEIGHT,
                      fg_color=COLOR_DISABLED_BG).pack(side="left")

    def _delete_lesson(self, engine, lesson_id):
        engine.delete_lesson(lesson_id)
        self.show_schedule_view()  # Перерисовать

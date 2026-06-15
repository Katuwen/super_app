# Окна и виджеты (Главное окно + окна утилит)

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.utils.currency_tracker import CurrencyTracker, plot_currency_dynamics
from app.utils.expense_manager import BudgetManager
from datetime import datetime
from app.utils.habit_tracker import HabitTracker


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SuperApp v1.0")
        self.geometry("1000x700")
        self.minsize(800, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- БОКОВАЯ ПАНЕЛЬ ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="SUPER APP",
            font=ctk.CTkFont(size=24, weight="bold"), text_color="#2b6cb0"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 0))

        self.btn_currency = ctk.CTkButton(
            self.sidebar_frame,
            text="💱 Курс Валют",
            command=self.show_currency_view,
            height=40
        )
        self.btn_currency.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_expenses = ctk.CTkButton(
            self.sidebar_frame,
            text="💰 Расходы",
            command=self.show_expense_view,
            height=40
        )
        self.btn_expenses.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_crypto = ctk.CTkButton(
            self.sidebar_frame, text="🪙 Крипто (Скоро)", state="disabled",
            fg_color="#555", height=40
        )
        self.btn_crypto.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_habits = ctk.CTkButton(
            self.sidebar_frame,
            text="✅ Привычки",
            command=self.show_habit_view,
            height=40
        )
        self.btn_habits.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # --- ОБЛАСТЬ КОНТЕНТА ---
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent"
        )
        self.content_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=20,
            pady=20
        )

        self.show_currency_view()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_currency_view(self):
        self.clear_content()
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        title = ctk.CTkLabel(
            container,
            text="Динамика курса валют (ЦБ РФ)",
            font=("Arial", 18, "bold")
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
                        font=("Arial", 14), text_color="green"
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
                        text_color="orange").pack(pady=20)
            else:
                ctk.CTkLabel(container,
                             text="⚠️ Не удалось загрузить данные ЦБ.",
                             font=("Arial", 14)).pack(pady=20)
        except Exception as e:
            ctk.CTkLabel(container,
                         text=f"Ошибка: {e}",
                         text_color="red").pack(pady=20)

    def show_expense_view(self):
        self.clear_content()
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container,
                     text="Учёт расходов",
                     font=("Arial", 18, "bold")).pack(pady=(0, 15))

        try:
            manager = BudgetManager()
            balance = manager.get_balance()

            # Баланс
            bal_frame = ctk.CTkFrame(
                container,
                fg_color=("#d4edda", "#1b4332")
            )
            bal_frame.pack(pady=10, padx=20, fill="x")
            ctk.CTkLabel(bal_frame,
                         text="Текущий баланс:",
                         font=("Arial", 12)).pack(side="left", padx=10)
            bal_color = "green" if balance >= 0 else "red"
            ctk.CTkLabel(bal_frame,
                         text=f"{balance:,.2f} ₽",
                         font=("Arial", 16, "bold"),
                         text_color=bal_color).pack(
                side="right", padx=10)

            # Форма ввода
            form = ctk.CTkFrame(container, fg_color="transparent")
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
                                     text_color="orange").pack(pady=5)
                except ValueError:
                    ctk.CTkLabel(container,
                                 text="⚠️ Ошибка формата числа",
                                 text_color="red").pack(pady=5)

            ctk.CTkButton(form,
                          text="➕ Добавить",
                          command=on_add,
                          width=110).grid(row=0,
                                          column=6,
                                          padx=10)

            # Нижняя часть: История + График
            bottom = ctk.CTkFrame(container, fg_color="transparent")
            bottom.pack(fill="both", expand=True, pady=10)

            # Список транзакций
            list_frame = ctk.CTkFrame(bottom, fg_color="#2b2b2b")
            list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            ctk.CTkLabel(list_frame,
                         text="Последние операции",
                         font=("Arial", 14, "bold")).pack(pady=5)

            scroll_trans = ctk.CTkScrollableFrame(list_frame, height=250)
            scroll_trans.pack(fill="both", expand=True, padx=5, pady=5)

            for t in manager.get_last_10_transactions():
                sign = "+" if t["type"] == "income" else "-"
                color = "green" if t["type"] == "income" else "red"
                row = ctk.CTkFrame(scroll_trans, fg_color="transparent")
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
                             font=("Arial", 12, "bold")).pack(side="right")

            # График
            chart_frame = ctk.CTkFrame(bottom, fg_color="#2b2b2b")
            chart_frame.pack(side="right",
                             fill="both",
                             expand=True,
                             padx=(5, 0))
            ctk.CTkLabel(chart_frame,
                         text="Диаграмма расходов",
                         font=("Arial", 14, "bold")).pack(pady=5)

            fig = manager.plot_expenses_pie()
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            ctk.CTkLabel(container,
                         text=f"Ошибка инициализации модуля: {e}",
                         text_color="red").pack(pady=20)

    def show_habit_view(self):
        self.clear_content()
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container, text="Трекер привычек", font=("Arial", 18, "bold")).pack(pady=10)

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
                ctk.CTkLabel(container, text="Введите название", text_color="orange").pack(pady=2)

        ctk.CTkButton(add_frame, text="➕ Добавить", command=add_habit).pack(side="left", padx=5)

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
                    width=100,
                    state="normal" if not already_done else "disabled",
                    command=lambda hid=habit["id"]: self._mark_habit_and_refresh(hid, tracker)
                )
                btn_mark.pack(side="left", padx=5)

                streak = tracker.get_current_streak(habit["id"])
                ctk.CTkLabel(habit_frame, text=f"🔥 {streak} дн.").pack(side="left", padx=5)

                ctk.CTkButton(
                    habit_frame,
                    text="🗑️",
                    width=30,
                    fg_color="#e74c3c",
                    hover_color="#c0392b",
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
                ctk.CTkLabel(container, text=f"График не загружен: {e}", text_color="red").pack()

    def _mark_habit_and_refresh(self, habit_id: int, tracker):
        try:
            tracker.mark_habit(habit_id, "done")
            self.show_habit_view()
        except ValueError as e:
            ctk.CTkLabel(self.content_frame, text=str(e), text_color="red").pack(pady=5)

    def _delete_habit_and_refresh(self, habit_id: int, tracker):
        tracker.delete_habit(habit_id)
        self.show_habit_view()

    def show_placeholder(self, name):
        self.clear_content()
        label = ctk.CTkLabel(self.content_frame,
                             text=f"Модуль '{name}' в разработке...",
                             font=("Arial", 20))
        label.pack(expand=True)

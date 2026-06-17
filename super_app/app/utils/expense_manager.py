# Заглушка для Утилиты 3


import json
import os
from datetime import datetime
from typing import List, Dict
import matplotlib.pyplot as plt


class BudgetManager:
    def __init__(self, data_file: str = "budget_data.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(base_dir, "..", "..", "data", data_file)
        self.data = self._load_data()

    def _load_data(self) -> dict:
        default_data = {
            "balance": 0.0,
            "transactions": [],
            "categories": ["Еда",
                           "Транспорт",
                           "Развлечения",
                           "Учеба",
                           "Здоровье",
                           "Прочее"],
            "goals": []
        }
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Гарантируем наличие всех полей при обновлениях структуры
                    for k, v in default_data.items():
                        loaded.setdefault(k, v)
                    return loaded
            except Exception:
                return default_data
        return default_data

    def save_data(self) -> None:
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def add_transaction(self,
                        amount: float,
                        category: str,
                        trans_type: str = "expense") -> bool:
        """Добавляет транзакцию. Возвращает True при успехе."""
        try:
            amount = float(amount)
            if amount <= 0:
                return False
        except (ValueError, TypeError):
            return False

        if trans_type == "income":
            self.data["balance"] += amount
        else:
            self.data["balance"] -= amount

        transaction = {
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "amount": amount,
            "category": category,
            "type": trans_type
        }
        self.data["transactions"].insert(0, transaction)
        # Храним последние 100 операций
        if len(self.data["transactions"]) > 100:
            self.data["transactions"].pop()
        self.save_data()
        return True

    def get_last_10_transactions(self) -> List[Dict]:
        return self.data["transactions"][:10]

    def get_balance(self) -> float:
        return self.data["balance"]

    def get_categories(self) -> List[str]:
        return self.data["categories"]

    def add_category(self, name: str) -> None:
        if name and name not in self.data["categories"]:
            self.data["categories"].append(name)
            self.save_data()

    def get_expenses_by_category_current_month(self) -> Dict[str, float]:
        """Собирает расходы по категориям за текущий месяц с корректным парсингом дат"""
        now = datetime.now()
        current_year, current_month = now.year, now.month
        expenses: dict[str, float] = {}

        for t in self.data["transactions"]:
            if t.get("type") != "expense":
                continue
            try:
                t_date = datetime.strptime(t["date"], "%d.%m.%Y %H:%M")
                if t_date.year == current_year and t_date.month == current_month:
                    cat = t["category"]
                    expenses[cat] = expenses.get(cat, 0.0) + t["amount"]
            except (ValueError, KeyError):
                continue
        return expenses

    def plot_expenses_pie(self) -> plt.Figure:
        """Строит круговую диаграмму расходов за текущий месяц"""
        data = self.get_expenses_by_category_current_month()
        fig, ax = plt.subplots(figsize=(5, 5))

        # Настройка под тёмную тему (опционально, но улучшает вид в dark mode)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        if not data:
            ax.text(0.5, 0.5, 'Нет расходов в этом месяце',
                    ha='center', va='center', fontsize=12, color='lightgray')
            ax.axis('off')
            return fig

        labels = list(data.keys())
        sizes = list(data.values())
        wedges, texts, autotexts = ax.pie(  # type: ignore
            sizes, labels=labels, autopct='%1.1f%%', startangle=90,
            textprops={'color': 'white', 'fontsize': 10}
        )
        ax.set_title('Расходы за текущий месяц', color='white', pad=15)
        fig.tight_layout()
        return fig

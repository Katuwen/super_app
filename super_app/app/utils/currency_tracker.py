import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from typing import Optional
from matplotlib.dates import date2num


def plot_currency_dynamics(currency_code: str = "USD", days: int = 7) -> plt.Figure:
    """Строит график динамики за последние N дней (демо-данные)"""
    dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]
    values = [75.0 + (i * 0.5) for i in range(days)]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(date2num(dates), values, marker='o', linestyle='-', color='#2b6cb0')
    ax.set_title(f'Динамика курса {currency_code} (РФ)')
    ax.set_xlabel('Дата')
    ax.set_ylabel('Курс (RUB)')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    return fig


class CurrencyTracker:
    def __init__(self) -> None:
        self.base_url = "https://www.cbr.ru/scripts/XML_daily.asp"

    def get_current_rates(self) -> Optional[pd.DataFrame]:
        """Получает текущие курсы ЦБ РФ и возвращает DataFrame"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()

            xml_string = response.content.decode('windows-1251')

            df = pd.read_xml(io.StringIO(xml_string),
                             xpath=".//Valute",
                             parser="etree")

            if df is not None and not df.empty:
                # ЦБ использует запятую как десятичный разделитель ("74,5678")
                df['Value'] = df['Value'].astype(str).str.replace(',',
                                                                  '.',
                                                                  regex=False)
                df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

                # Алиас для совместимости с views.py
                df['ValCurs'] = df['Value']

                # Возвращаем только нужные колонки
                return df[['CharCode', 'Name', 'Value', 'ValCurs']]

            return pd.DataFrame()

        except UnicodeDecodeError as e:
            print(f"❌ Ошибка кодировки (ожидалась windows-1251): {e}")
            return None
        except requests.RequestException as e:
            print(f"❌ Ошибка сети: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка парсинга/обработки: {e}")
            return None

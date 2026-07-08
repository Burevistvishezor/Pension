import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Официальные экономические показатели Германии на 2026 год
AVERAGE_ANNUAL_EARNINGS = 50550.0  # Средняя зарплата в ФРГ для 1 балла
PENSION_POINT_VALUE = 39.32        # Стоимость одного балла (Rentenwert)

class PensionFundCore:
    def __init__(self, db_name="german_pension.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        self.seed_sample_data()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                insurance_number TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                birth_date TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contribution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insurance_number TEXT,
                year INTEGER,
                annual_income REAL,
                FOREIGN KEY(insurance_number) REFERENCES clients(insurance_number)
            )
        """)
        self.conn.commit()

    def seed_sample_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        if cursor.fetchone() == 0:
            cursor.execute("INSERT INTO clients VALUES ('RV-19700512-K-042', 'Kamil', 'Aliev', '1970-05-12')")
            history = [
                ('RV-19700512-K-042', 2021, 45000.0),
                ('RV-19700512-K-042', 2022, 48000.0),
                ('RV-19700512-K-042', 2023, 52000.0),
                ('RV-19700512-K-042', 2024, 55000.0),
                ('RV-19700512-K-042', 2025, 59000.0),
            ]
            cursor.executemany("INSERT INTO contribution_history (insurance_number, year, annual_income) VALUES (?, ?, ?)", history)
            self.conn.commit()

    def get_client_analytics(self, insurance_number):
        """Аналитический блок на Pandas."""
        query = f"SELECT year, annual_income FROM contribution_history WHERE insurance_number = '{insurance_number}' ORDER BY year"
        df = pd.read_sql_query(query, self.conn)
        
        if df.empty:
            return None

        # Расчет баллов и прогнозной пенсии
        df['rentenpunkte'] = df['annual_income'] / AVERAGE_ANNUAL_EARNINGS
        df['estimated_monthly_pension'] = df['rentenpunkte'] * PENSION_POINT_VALUE
        
        # Накопительный итог (Кумулятивная сумма для графиков)
        df['cumulative_points'] = df['rentenpunkte'].cumsum()
        df['cumulative_pension'] = df['estimated_monthly_pension'].cumsum()

        total_points = df['rentenpunkte'].sum()
        total_pension = df['estimated_monthly_pension'].sum()
        
        return df, total_points, total_pension

    def plot_pension_trend(self, df):
        """Создание аналитического графика и сохранение на ПК."""
        plt.figure(figsize=(10, 5))
        
        # Строим линию роста будущей пенсии по годам
        plt.plot(df['year'].astype(str), df['cumulative_pension'], marker='o', color='#007ec6', linewidth=2.5, label='Monthly Pension (€)')
        
        # Настройки красивого немецкого интерфейса графика
        plt.title('Deutsche Rentenversicherung - Future Pension Growth Trend', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Year of Contribution', fontsize=12)
        plt.ylabel('Estimated Monthly Payout (€)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # Добавляем подписи значений над каждой точкой
        for x, y in zip(df['year'].astype(str), df['cumulative_pension']):
            plt.text(x, y + 2, f"{y:.2f} €", ha='center', va='bottom', fontsize=10, fontweight='bold')
            
        plt.legend(loc='upper left')
        plt.tight_layout()
        
        # Сохраняем файл на диск
        filename = "pension_trend.png"
        plt.savefig(filename, dpi=300)
        plt.close()
        return filename

    def make_voluntary_contribution(self, insurance_number, amount):
        current_year = datetime.now().year
        cursor = self.conn.cursor()
        
        cursor.execute(
            "SELECT id, annual_income FROM contribution_history WHERE insurance_number = ? AND year = ?", 
            (insurance_number, current_year)
        )
        row = cursor.fetchone()
        
        if row:
            new_income = row[1] + amount
            cursor.execute("UPDATE contribution_history SET annual_income = ? WHERE id = ?", (new_income, row[0]))
        else:
            cursor.execute(
                "INSERT INTO contribution_history (insurance_number, year, annual_income) VALUES (?, ?, ?)",
                (insurance_number, current_year, amount)
            )
        self.conn.commit()
        return True

def main():
    core = PensionFundCore()
    my_rv_number = 'RV-19700512-K-042'

    print("=== Deutsche Rentenversicherung (DRV) - Analytic Portal ===")
    
    while True:
        print("\n1. View my Pension Account Analytics (SQL + Pandas)")
        print("2. Generate & Save Pension Growth Chart (Matplotlib Data Viz)")
        print("3. Make a Voluntary Pension Contribution")
        print("4. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            df, total_pts, total_pension = core.get_client_analytics(my_rv_number)
            print("\n--- Contribution History Breakdown ---")
            print(df[['year', 'annual_income', 'rentenpunkte', 'estimated_monthly_pension']].to_string(index=False))
            print("---------------------------------------------------------")
            print(f"Total Accumulated Rentenpunkte: {total_pts:.4f}")
            print(f"Current Estimated Monthly Pension: {total_pension:.2f} €")
            
        elif choice == "2":
            df, _, _ = core.get_client_analytics(my_rv_number)
            file_saved = core.plot_pension_trend(df)
            print(f"\n[SUCCESS] Analytics chart generated and saved as: '{file_saved}'")
            print("You can open this image on your PC to view your pension growth trend line.")
            
        elif choice == "3":
            try:
                amount = float(input("\nEnter contribution amount in €: "))
                if amount <= 0: raise ValueError
                core.make_voluntary_contribution(my_rv_number, amount)
                print(f"Success! Credited {amount} € to your account.")
            except ValueError:
                print("Invalid amount.")
                
        elif choice == "4":
            print("Auf Wiedersehen!")
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()

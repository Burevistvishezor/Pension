# Pension
Data Visualization
## Key Features
* **Data Access Layer:** Uses `sqlite3` to model relational schemas for client registration and transactional contribution history.
* **FinTech Analytics Layer (Pandas):** Implements automated calculations of official German Pension Points (*Rentenpunkte*) based on statutory average earnings.
* **Data Visualization (Matplotlib):** Generates and exports high-resolution line charts representing the cumulative growth trend of the user's future monthly pension payouts.
* **Account Manipulation:** Simulates voluntary user contributions (*Freiwillige Beiträge*) with atomic SQL transactions.

## Setup Requirements
1. `pip install pandas matplotlib`
2. Run `python pension_core.py` and select option 2 to generate the trend chart.
plot_pension_trend.

![German Pension Growth Trend](pension_trend.png)

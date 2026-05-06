import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

# ── Config ────────────────────────────────────────────────────────────────────
DB_PATH = '../AdventureWorks.db'
CSV_OUTPUT_DIR = '../outputs'
RUN_TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

# ── Setup ─────────────────────────────────────────────────────────────────────
os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
def load_data(db_path):
    print("Loading data from database...")
    conn = sqlite3.connect(db_path)

    internet = pd.read_sql("""
        SELECT 
            s.SalesAmount,
            s.OrderQuantity,
            s.UnitPrice,
            s.DiscountAmount,
            s.UnitPriceDiscountPct,
            s.OrderDateKey,
            s.SalesTerritoryKey,
            s.PromotionKey,
            'Internet' as Source
        FROM FactInternetSales s
    """, conn)

    reseller = pd.read_sql("""
        SELECT 
            s.SalesAmount,
            s.OrderQuantity,
            s.UnitPrice,
            s.DiscountAmount,
            s.UnitPriceDiscountPct,
            s.OrderDateKey,
            s.SalesTerritoryKey,
            s.PromotionKey,
            'Reseller' as Source
        FROM FactResellerSales s
    """, conn)

    conn.close()
    df = pd.concat([internet, reseller], ignore_index=True)
    print(f"Data loaded successfully — {df.shape[0]} rows, {df.shape[1]} columns")
    return df

# ── Feature Engineering ───────────────────────────────────────────────────────
def engineer_features(df):
    print("Engineering features...")
    df['Year'] = df['OrderDateKey'].astype(str).str[:4].astype(int)
    df['Month'] = df['OrderDateKey'].astype(str).str[4:6].astype(int)
    df['IsInternet'] = (df['Source'] == 'Internet').astype(int)
    df_model = df.drop(columns=['OrderDateKey', 'Source'])
    print(f"Features ready — {df_model.shape[1]} columns")
    return df_model

# ── Regression ────────────────────────────────────────────────────────────────
def run_regression(df, target):
    print(f"\nRunning regression for target: {target}")
    X = df.drop(columns=['SalesAmount', 'OrderQuantity'])
    y = df[target]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"R² Score:  {r2:.4f}")
    print(f"RMSE:      {rmse:.4f}")

    # Statsmodels summary
    X_sm = sm.add_constant(X_scaled)
    sm_model = sm.OLS(y, X_sm).fit()

    # Feature coefficients
    coef_df = pd.DataFrame({
        'Target': target,
        'Feature': X.columns,
        'Coefficient': model.coef_,
        'R2_Score': r2,
        'RMSE': rmse,
        'Run_Timestamp': RUN_TIMESTAMP
    }).sort_values('Coefficient', ascending=False)

    return model, scaler, coef_df, r2, rmse

# ── Save Results ──────────────────────────────────────────────────────────────
def save_results(results_df, db_path, csv_dir):
    # Save to CSV
    csv_path = os.path.join(csv_dir, f'regression_results_{RUN_TIMESTAMP}.csv')
    results_df.to_csv(csv_path, index=False)
    print(f"\nCSV saved to: {csv_path}")

    # Save to SQLite
    conn = sqlite3.connect(db_path)
    results_df.to_sql(
        'RegressionResults',
        conn,
        if_exists='append',
        index=False
    )
    conn.close()
    print("Results saved to RegressionResults table in database")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("AdventureWorks Regression Pipeline")
    print(f"Run: {RUN_TIMESTAMP}")
    print("=" * 50)

    df = load_data(DB_PATH)
    df_model = engineer_features(df)

    all_results = []

    for target in ['SalesAmount', 'OrderQuantity']:
        model, scaler, coef_df, r2, rmse = run_regression(df_model, target)
        all_results.append(coef_df)

    results_df = pd.concat(all_results, ignore_index=True)
    save_results(results_df, DB_PATH, CSV_OUTPUT_DIR)

    print("\n" + "=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
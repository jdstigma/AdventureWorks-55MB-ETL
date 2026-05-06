import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
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
    print(f"Data loaded — {df.shape[0]} rows, {df.shape[1]} columns")
    return df

# ── Feature Engineering ───────────────────────────────────────────────────────
def engineer_features(df):
    print("Engineering features...")
    df['Year'] = df['OrderDateKey'].astype(str).str[:4].astype(int)
    df['Month'] = df['OrderDateKey'].astype(str).str[4:6].astype(int)
    df['IsInternet'] = (df['Source'] == 'Internet').astype(int)
    df['RevenuePerUnit'] = (
        df['SalesAmount'] / df['OrderQuantity']
    ).replace([np.inf, -np.inf], 0).fillna(0)
    df['DiscountFlag'] = (df['DiscountAmount'] > 0).astype(int)
    df['Quarter'] = pd.cut(
        df['Month'],
        bins=[0, 3, 6, 9, 12],
        labels=[1, 2, 3, 4]
    ).astype(int)
    mean_sales = df['SalesAmount'].mean()
    df['HighValueFlag'] = (df['SalesAmount'] > mean_sales).astype(int)
    df['DiscountIntensity'] = pd.cut(
        df['UnitPriceDiscountPct'],
        bins=[-0.01, 0, 0.1, 0.2, 0.4, 1.0],
        labels=[0, 1, 2, 3, 4]
    ).astype(int)
    df = df.drop(columns=['OrderDateKey', 'Source'])
    print(f"Features ready — {df.shape[1]} columns")
    return df

# ── Bucket Quantity ───────────────────────────────────────────────────────────
def bucket_quantity(q):
    if q == 1:
        return 'Single'
    elif q <= 10:
        return 'Small_Medium'
    elif q <= 20:
        return 'Large'
    else:
        return 'Bulk'

# ── Random Forest Regression ──────────────────────────────────────────────────
def run_rf_regression(df, target='SalesAmount'):
    print(f"\nRunning Random Forest Regression — {target}")
    
    # Drop leakage columns
    df_clean = df.drop(columns=['HighValueFlag', 'RevenuePerUnit'])
    X = df_clean.drop(columns=['SalesAmount', 'OrderQuantity'])
    y = df_clean[target]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"R2 Score:  {r2:.4f}")
    print(f"RMSE:      {rmse:.4f}")
    
    # Cross Validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_r2 = cross_val_score(rf, X_scaled, y, cv=kf, scoring='r2')
    cv_rmse = cross_val_score(rf, X_scaled, y, cv=kf,
                               scoring='neg_root_mean_squared_error')
    
    print(f"CV R2 Mean:    {cv_r2.mean():.4f} (+/- {cv_r2.std():.4f})")
    print(f"CV RMSE Mean:  {abs(cv_rmse.mean()):.4f} (+/- {abs(cv_rmse.std()):.4f})")
    
    # Feature importance
    importance_df = pd.DataFrame({
        'Target': target,
        'Feature': X.columns,
        'Importance': rf.feature_importances_,
        'R2_Score': r2,
        'CV_R2_Mean': cv_r2.mean(),
        'RMSE': rmse,
        'CV_RMSE_Mean': abs(cv_rmse.mean()),
        'Run_Timestamp': RUN_TIMESTAMP
    }).sort_values('Importance', ascending=False)
    
    return rf, scaler, importance_df

# ── Bucketed Classifier ───────────────────────────────────────────────────────
def run_bucketed_classifier(df):
    print(f"\nRunning Bucketed Classifier — OrderQuantity")
    
    df_cls = df.drop(columns=['HighValueFlag', 'RevenuePerUnit']).copy()
    df_cls['OrderQuantityBucket'] = df_cls['OrderQuantity'].apply(bucket_quantity)
    df_cls = df_cls.drop(columns=['OrderQuantity'])
    
    X = df_cls.drop(columns=['SalesAmount', 'OrderQuantityBucket'])
    y = df_cls['OrderQuantityBucket']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy:  {accuracy:.4f}")
    print(classification_report(y_test, y_pred))
    
    # Cross Validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_acc = cross_val_score(clf, X_scaled, y, cv=kf, scoring='accuracy')
    cv_f1 = cross_val_score(clf, X_scaled, y, cv=kf, scoring='f1_weighted')
    
    print(f"CV Accuracy Mean:  {cv_acc.mean():.4f} (+/- {cv_acc.std():.4f})")
    print(f"CV F1 Mean:        {cv_f1.mean():.4f} (+/- {cv_f1.std():.4f})")
    
    importance_df = pd.DataFrame({
        'Target': 'OrderQuantityBucket',
        'Feature': X.columns,
        'Importance': clf.feature_importances_,
        'Accuracy': accuracy,
        'CV_Accuracy_Mean': cv_acc.mean(),
        'CV_F1_Mean': cv_f1.mean(),
        'Run_Timestamp': RUN_TIMESTAMP
    }).sort_values('Importance', ascending=False)
    
    return clf, scaler, importance_df

# ── Save Results ──────────────────────────────────────────────────────────────
def save_results(results_df, db_path, csv_dir):
    csv_path = os.path.join(csv_dir, f'regression_results_{RUN_TIMESTAMP}.csv')
    results_df.to_csv(csv_path, index=False)
    print(f"\nCSV saved to: {csv_path}")
    
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
    df = engineer_features(df)
    
    all_results = []
    
    # Random Forest Regression
    rf_reg, scaler_reg, reg_results = run_rf_regression(df, 'SalesAmount')
    all_results.append(reg_results)
    
    # Bucketed Classifier
    clf, scaler_clf, cls_results = run_bucketed_classifier(df)
    all_results.append(cls_results)
    
    # Save all results
    results_df = pd.concat(all_results, ignore_index=True)
    save_results(results_df, DB_PATH, CSV_OUTPUT_DIR)
    
    print("\n" + "=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
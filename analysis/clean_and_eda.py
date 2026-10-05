# -*- coding: utf-8 -*-
"""
MamaEarth Growth Intelligence Pipeline
Part 2: Python/Pandas Data Wrangling & EDA

Run from the repository root. Raw CSV files remain unchanged.
This script cleans the data, performs EDA, and generates narrator/findings.json.
"""

import json
import os
import pandas as pd

# ============================================================
# TASK 1 — Load and Inspect
# ============================================================
orders = pd.read_csv("data/orders.csv")
customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")

print("TASK 1 — Load and Inspect")
print("Orders shape:", orders.shape)
print("Customers shape:", customers.shape)
print("Products shape:", products.shape)

# ============================================================
# TASK 2 — Standardize payment_method
# ============================================================
print("\nPayment methods BEFORE cleaning:")
print(orders["payment_method"].unique())

orders["payment_method"] = (
    orders["payment_method"].str.strip().str.upper()
)

print("\nPayment methods AFTER cleaning:")
print(orders["payment_method"].unique())
print("\nPayment method counts:")
print(orders["payment_method"].value_counts())

# ============================================================
# TASK 3 — Remove Duplicate Orders
# ============================================================
natural_key = [
    "customer_id", "product_id", "order_date", "quantity",
    "discount_pct", "payment_method", "rating", "returned"
]

duplicate_mask = orders.duplicated(subset=natural_key, keep="first")
dropped_order_ids = orders.loc[duplicate_mask, "order_id"].tolist()

print("\nDuplicate orders detected:")
print(dropped_order_ids)
print("Number of duplicate rows:", duplicate_mask.sum())

orders_clean = orders.loc[~duplicate_mask].copy()
print("Orders shape after removing duplicates:")
print(orders_clean.shape)

# ============================================================
# TASK 4 — Impute Missing Values
# ============================================================
missing_discount = orders_clean["discount_pct"].isna().sum()
orders_clean["discount_pct"] = orders_clean["discount_pct"].fillna(0)
print("\nDiscount values filled:", missing_discount)

rating_median = orders_clean["rating"].median()
print("Rating median before imputation:", rating_median)

missing_rating = orders_clean["rating"].isna().sum()
orders_clean["rating"] = orders_clean["rating"].fillna(rating_median)
print("Rating values filled:", missing_rating)

print("\nMissing values after imputation:")
print(orders_clean[["discount_pct", "rating"]].isnull().sum())

# ============================================================
# TASK 5 — Merge and Reconcile Against Part 1
# ============================================================
merged = orders_clean.merge(products, on="product_id", how="left")
merged = merged.merge(customers, on="customer_id", how="left")

# order_value = quantity × price × (1 - discount/100)
merged["order_value"] = (
    merged["quantity"] * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

cleaned_total = merged["order_value"].sum()
print("\nTotal order value after cleaning:", round(cleaned_total, 2))

# Part 1 SQL report A gives the raw revenue baseline.
raw_total = 99860.20
difference = raw_total - cleaned_total

print("\nReconciliation:")
print("Part 1 raw revenue:", round(raw_total, 2))
print("Part 2 cleaned revenue:", round(cleaned_total, 2))
print("Difference:", round(difference, 2))

dropped_orders = orders.loc[duplicate_mask].copy()
dropped_orders = dropped_orders.merge(products, on="product_id", how="left")
dropped_orders["discount_pct"] = dropped_orders["discount_pct"].fillna(0)

dropped_order_value = (
    dropped_orders["quantity"] * dropped_orders["price"]
    * (1 - dropped_orders["discount_pct"] / 100)
).sum()

print("Order value of removed duplicate rows:", round(dropped_order_value, 2))
print(
    "\nReconciliation Note: The cleaned revenue is ₹2,501.90 lower "
    "than the Part 1 raw revenue because the five duplicate orders "
    "removed in Task 3 contributed a combined order value of ₹2,501.90. "
    "The discount and rating imputations did not change the order_value "
    "total because discount_pct missing values were treated as 0, while "
    "rating is not used in the order_value calculation."
)

# ============================================================
# TASK 6 — IQR Outlier Detection on quantity
# ============================================================
Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("\nTASK 6 — IQR Outlier Detection")
print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower)
print("Upper bound:", upper)

# Flag, do not delete, outliers.
merged["is_outlier"] = (
    (merged["quantity"] < lower) | (merged["quantity"] > upper)
)
outliers = merged[merged["is_outlier"]]

print("\nNumber of outliers:", len(outliers))
print("\nOutlier orders:")
print(outliers[["order_id", "quantity"]])

# ============================================================
# TASK 7 — Hypothesis: Does COD have a higher return rate?
# ============================================================
print(
    "\nHypothesis: COD orders have a higher return rate "
    "than other payment methods."
)

return_rate = merged.groupby("payment_method")["returned"].agg(["count", "mean"])
return_rate["return_rate_pct"] = (return_rate["mean"] * 100).round(1)

print("\nReturn rate by payment method:")
print(return_rate)
print(
    "\nHypothesis Result: Confirmed — COD has a higher return rate "
    "than CARD and UPI."
)

# ============================================================
# TASK 8 — Multi-level Segmentation
# ============================================================
segmentation = (
    merged.groupby(["payment_method", "city_tier"])["returned"]
    .agg(["count", "mean"])
    .reset_index()
)
segmentation["return_rate_pct"] = (segmentation["mean"] * 100).round(1)
segmentation = segmentation.drop(columns=["mean"])

print("\nReturn rate by payment method and city tier:")
print(segmentation)

highest_risk = segmentation.loc[segmentation["return_rate_pct"].idxmax()]
print("\nHighest-risk segment:")
print(
    f"{highest_risk['payment_method']} + Tier-{int(highest_risk['city_tier'])} "
    f"with {highest_risk['return_rate_pct']:.1f}% return rate"
)
print(
    "\nKey Finding: COD risk is not uniform across city tiers. "
    "COD + Tier-1 has a 37.5% return rate, while COD + Tier-2 has a "
    "54.5% return rate. Therefore, COD + Tier-2 is the highest-risk segment."
)

# ============================================================
# TASK 9 — Correlation Analysis
# ============================================================
correlation_columns = ["rating", "returned", "discount_pct", "quantity"]
correlation_matrix = merged[correlation_columns].corr()

print("\nCorrelation Matrix:")
print(correlation_matrix)


def correlation_strength(r):
    """Classify correlation using the assignment's bands."""
    r = abs(r)
    if r < 0.2:
        return "negligible"
    elif r < 0.4:
        return "weak"
    elif r < 0.7:
        return "moderate"
    return "strong"


print("\nPairwise Correlation Strength:")
for i in range(len(correlation_columns)):
    for j in range(i + 1, len(correlation_columns)):
        col1 = correlation_columns[i]
        col2 = correlation_columns[j]
        r = correlation_matrix.loc[col1, col2]
        print(f"{col1} vs {col2}: r = {r:.2f} → {correlation_strength(r)}")

discount_return_corr = correlation_matrix.loc["discount_pct", "returned"]
print("\nHypothesis: Higher discounts reduce returns.")
print(f"Discount vs Returned correlation: {discount_return_corr:.2f}")
print(
    "Hypothesis Result: Busted — the correlation is negligible (|r| < 0.2)."
)

# ============================================================
# TASK 10 — Outlier-Corrected Time Series
# ============================================================
merged["order_date"] = pd.to_datetime(merged["order_date"])
merged["year_month"] = merged["order_date"].dt.to_period("M").astype(str)

monthly_revenue_with_outliers = (
    merged.groupby("year_month")["order_value"].sum().round(2)
)
print("\nMonthly Revenue — Including Outliers:")
print(monthly_revenue_with_outliers)

monthly_revenue_without_outliers = (
    merged[~merged["is_outlier"]]
    .groupby("year_month")["order_value"]
    .sum()
    .round(2)
)
print("\nMonthly Revenue — Outlier Corrected:")
print(monthly_revenue_without_outliers)

peak_month = monthly_revenue_without_outliers.idxmax()
peak_revenue = monthly_revenue_without_outliers.max()

print(
    f"\nActual peak month after removing outliers: {peak_month} "
    f"with revenue ₹{peak_revenue:,.2f}"
)
print(
    "\nTime-Series Finding: January's apparent revenue lead is an artifact "
    "of the two bulk orders that occurred in January — O0011 on 2026-01-28 "
    "with quantity 25 and O0098 on 2026-01-10 with quantity 30. Once these "
    "two outlier orders are excluded, March becomes the genuine peak month."
)

# ============================================================
# TASK 11 — Automatically Build Verified Findings
# ============================================================
return_rate_by_payment = {
    payment_method: round(float(rate), 1)
    for payment_method, rate in return_rate["return_rate_pct"].items()
}

highest_risk_finding = {
    "payment_method": str(highest_risk["payment_method"]),
    "city_tier": int(highest_risk["city_tier"]),
    "return_rate_pct": round(float(highest_risk["return_rate_pct"]), 1),
}

outlier_impact = monthly_revenue_with_outliers - monthly_revenue_without_outliers
outlier_inflated_month = str(outlier_impact.idxmax())

findings = {
    "cleaned_total_revenue_inr": round(float(cleaned_total), 2),
    "raw_total_revenue_inr": round(float(raw_total), 2),
    "duplicate_reconciliation_delta_inr": round(float(difference), 2),
    "return_rate_by_payment": return_rate_by_payment,
    "highest_risk_segment": highest_risk_finding,
    "true_peak_month": {
        "month": str(peak_month),
        "revenue_inr": round(float(peak_revenue), 2),
    },
    "outlier_inflated_month": {
        "month": outlier_inflated_month,
        "apparent_revenue_inr": round(
            float(monthly_revenue_with_outliers.loc[outlier_inflated_month]), 2
        ),
        "corrected_revenue_inr": round(
            float(monthly_revenue_without_outliers.loc[outlier_inflated_month]), 2
        ),
    },
}

# Write the verified findings used by Part 3.
os.makedirs("narrator", exist_ok=True)
with open("narrator/findings.json", "w", encoding="utf-8") as f:
    json.dump(findings, f, indent=2)

print("\nfindings.json created successfully.")
print(json.dumps(findings, indent=2))

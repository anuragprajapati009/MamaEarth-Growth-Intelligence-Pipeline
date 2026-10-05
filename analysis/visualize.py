"""
MamaEarth Growth Intelligence Pipeline
Part 2: Visualizations

This script reads the raw CSV files, applies the same verified cleaning
steps needed for the visualizations, and saves the required charts.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# LOAD RAW DATA
# ============================================================

orders = pd.read_csv("data/orders.csv")
customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")


# ============================================================
# PREPARE DATA FOR VISUALIZATION
# ============================================================

# Standardize payment-method values.
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

# Remove duplicate orders using the same natural key as clean_and_eda.py.
natural_key = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

duplicate_mask = orders.duplicated(
    subset=natural_key,
    keep="first"
)

orders_clean = orders.loc[~duplicate_mask].copy()

# Apply the same missing-value rule used in the EDA.
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

rating_median = orders_clean["rating"].median()
orders_clean["rating"] = (
    orders_clean["rating"].fillna(rating_median)
)

# Merge product and customer information.
merged = orders_clean.merge(
    products,
    on="product_id",
    how="left"
)

merged = merged.merge(
    customers,
    on="customer_id",
    how="left"
)

# Calculate order value.
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

# Detect quantity outliers using the same IQR method.
Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

merged["is_outlier"] = (
    (merged["quantity"] < lower)
    | (merged["quantity"] > upper)
)

# Prepare year-month values for the time series.
merged["order_date"] = pd.to_datetime(merged["order_date"])

merged["year_month"] = (
    merged["order_date"]
    .dt.to_period("M")
    .astype(str)
)


# Create the output folder.
os.makedirs("visualizations", exist_ok=True)


# ============================================================
# VISUALIZATION 1 — RETURN RATE BY PAYMENT METHOD
# ============================================================

payment_return_rate = (
    merged
    .groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("Return Rate by Payment Method:")
print(payment_return_rate.round(1))

plt.figure(figsize=(8, 5))

bars = plt.bar(
    payment_return_rate.index,
    payment_return_rate.values,
    color=["red", "blue", "green"]
)

for bar, value in zip(
    bars,
    payment_return_rate.values
):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.1f}%",
        ha="center",
        va="bottom"
    )

plt.title("COD Returns at 44.4% — 3x Card")
plt.xlabel("Payment Method")
plt.ylabel("Return Rate (%)")

plt.ylim(
    0,
    max(payment_return_rate.values) + 10
)

plt.tight_layout()

plt.savefig(
    "visualizations/return_rate_by_payment.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# VISUALIZATION 2 — OUTLIER-CORRECTED MONTHLY REVENUE
# ============================================================

monthly_revenue_without_outliers = (
    merged[~merged["is_outlier"]]
    .groupby("year_month")["order_value"]
    .sum()
    .round(2)
)

plt.figure(figsize=(10, 5))

plt.plot(
    monthly_revenue_without_outliers.index,
    monthly_revenue_without_outliers.values,
    marker="o",
    linewidth=2
)

for month, revenue in monthly_revenue_without_outliers.items():
    plt.text(
        month,
        revenue,
        f"₹{revenue:,.0f}",
        ha="center",
        va="bottom"
    )

plt.title(
    "Monthly Revenue Trend — March 2026 is the Actual Peak"
)

plt.xlabel("Month")
plt.ylabel("Revenue (₹)")

plt.xticks(rotation=45)
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    "visualizations/monthly_revenue_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nVisualizations created successfully.")

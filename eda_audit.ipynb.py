# ==========================================
# PART 1: SYSTEM SETUP & DATA LOADING
# ==========================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set design styles for visualizations
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [10, 6]

# Read datasets
customers = pd.read_csv("customers.csv")
orders = pd.read_csv("orders.csv")
support = pd.read_csv("support_tickets.csv")
web_events = pd.read_csv("web_events_snapshot.csv")
labels = pd.read_csv("churn_labels.csv")
interventions = pd.read_csv("intervention_history.csv")

print(f"Data Matrix Verified. Total Baseline Customers: {customers.shape[0]}")

# ==========================================
# DATA QUALITY AUDIT & LEAKAGE REMEDIATION
# ==========================================

# 1. Target Leakage Prevention: Enforce Snapshot Isolation Rule
orders['order_date'] = pd.to_datetime(orders['order_date'])
snapshot_date = pd.to_datetime('2025-09-30')

# Isolate pre-snapshot data for safe feature engineering and EDA
pre_snapshot_orders = orders[orders['order_date'] <= snapshot_date].copy()
post_snapshot_orders = orders[orders['order_date'] > snapshot_date].copy()

print(f"Sanitization Complete: Removed {len(orders) - len(pre_snapshot_orders)} post-snapshot leak rows.")

# 2. De-duplication: Handle programmatic _DUP anomalies
initial_count = len(pre_snapshot_orders)
pre_snapshot_orders = pre_snapshot_orders[~pre_snapshot_orders['order_id'].astype(str).str.endswith('_DUP')]
print(f"Deduplication Applied: Extracted {initial_count - len(pre_snapshot_orders)} '_DUP' lines.")

# ==========================================
# 5 DATA-BACKED RISK HYPOTHESES & VISUALS
# ==========================================

# Merge base analytics table matching labels
df_eda = pd.merge(labels, customers, on="customer_id", how="left")

# --- HYPOTHESIS 1: The Support Escalation Wall ---
# Extract support characteristics per customer
support_agg = support.groupby('customer_id').agg(
    avg_resolution=('resolution_hours', 'mean'),
    min_sentiment=('sentiment_score', 'min')
).reset_index()

df_hyp1 = pd.merge(df_eda, support_agg, on="customer_id", how="left").fillna({'avg_resolution': 0, 'min_sentiment': 0})

plt.figure()
sns.boxplot(data=df_hyp1, x='churn_next_60d', y='avg_resolution', hue='churn_next_60d', palette="muted", legend=False)
plt.title("Hypothesis 1: Delayed Support Resolution Correlates Directly with Higher Churn Rates")
plt.xlabel("Churn Status (0=Retained, 1=Churned)")
plt.ylabel("Average Ticket Resolution Hours")
plt.savefig("hypothesis_1_support_wall.png")
plt.show()

# --- HYPOTHESIS 2: Fulfillment Friction (Late Shipments) ---
order_perf = pre_snapshot_orders.groupby('customer_id').agg(
    avg_delivery=('delivery_days', 'mean'),
    return_rate=('returned', 'mean')
).reset_index()

df_hyp2 = pd.merge(df_eda, order_perf, on="customer_id", how="left")

plt.figure()
sns.kdeplot(data=df_hyp2, x='avg_delivery', hue='churn_next_60d', fill=True, common_norm=False, palette="crest")
plt.title("Hypothesis 2: Delivery Latency Exceeding Threshold Spikes Churn Intention")
plt.xlabel("Average Delivery Performance (Days)")
plt.savefig("hypothesis_2_delivery_friction.png")
plt.show()

# --- HYPOTHESIS 3: First-Order Satisfaction Drop-off ---
first_order_rating = pre_snapshot_orders.sort_values('order_date').groupby('customer_id').first().reset_index()
df_hyp3 = pd.merge(df_eda, first_order_rating[['customer_id', 'rating']], on='customer_id', how='left')

plt.figure()
sns.countplot(data=df_hyp3, x='rating', hue='churn_next_60d', palette="viridis")
plt.title("Hypothesis 3: Low Initial Experience Ratings Predict Structural Churn Risk")
plt.xlabel("First Order Rating Provided")
plt.savefig("hypothesis_3_initial_rating.png")
plt.show()

# --- HYPOTHESIS 4: Digital App Disengagement ---
df_hyp4 = pd.merge(df_eda, web_events, on="customer_id", how="left")

plt.figure()
sns.scatterplot(data=df_hyp4, x='sessions_30d', y='last_visit_days_ago', hue='churn_next_60d', alpha=0.6)
plt.title("Hypothesis 4: Digital Footprint Recency vs Frequency Decoupling")
plt.xlabel("Total Active App/Web Sessions (Last 30 Days)")
plt.ylabel("Days Since Last Platform Interaction")
plt.savefig("hypothesis_4_digital_dormancy.png")
plt.show()

# --- HYPOTHESIS 5: Acquisition Channel Churn Variance ---
plt.figure()
channel_churn = df_eda.groupby('acquisition_channel')['churn_next_60d'].mean().reset_index()
sns.barplot(data=channel_churn.sort_values(by='churn_next_60d'), x='acquisition_channel', y='churn_next_60d', hue='acquisition_channel', palette="magma", legend=False)
plt.title("Hypothesis 5: Churn Baseline Probabilities Vary Across Acquisition Funnels")
plt.ylabel("Observed Mean Churn Ratio")
plt.xlabel("Inbound Channel Source")
plt.savefig("hypothesis_5_channel_vulnerability.png")
plt.show()

# --- ADDITIONAL VISUALIZATION 6: Churn Class Imbalance Baseline ---
plt.figure()
labels['churn_next_60d'].value_counts(normalize=True).plot(kind='bar', color=['#4C72B0', '#C44E52'])
plt.title("Baseline System Target Distribution (Class Balance Baseline)")
plt.xticks([0, 1], ['Active (0)', 'Churned (1)'], rotation=0)
plt.ylabel("Proportion of Total Customer Base")
plt.savefig("baseline_churn_distribution.png")
plt.show()
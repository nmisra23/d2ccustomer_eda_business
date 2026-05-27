# Data Quality Audit Report

**Snapshot Date:** 2025-09-30  
**Status:** COMPLETE (Requires Target Leakage Enforcement & Deduplication)

## Executive Summary
An audit of the D2C Capstone dataset revealed specific data-quality challenges, including intentional duplicate keys (`_DUP`), severe missingness in optional customer metrics (`rating`), and target leakage vectors within transaction logs. Immediate programmatic remediation is required prior to Part 2 feature engineering.

---

## 1. Primary Key & Integrity Constraints
* **`customer_id` Consistency:** Holds a total unique customer universe of 2,395 records. Cross-file structural integrity is highly consistent, but activity distributions vary widely (e.g., not all customers have recorded support interactions).
* **`order_id` Duplications:** The transaction history (`orders.csv`) contains explicitly duplicated records appended with `_DUP`. These represent artificial duplicate-like line items that inflate gross transaction amounts and frequency calculations if unhandled.

## 2. Missingness & Completeness
* **`orders.rating`:** Approximately ~15-20% of orders lack customer satisfaction ratings. This requires treatment (e.g., flagging missingness as a category or using median values) rather than simple row dropping, to avoid discarding transactional histories.
* **`support_tickets.resolution_hours` / `sentiment_score`:** Missing for customers without recorded service tickets. These fields must be handled via right-joins/zero-filling where appropriate to capture "No Ticket" as a valid behavioral profile.

## 3. Outliers & Anomaly Detection
* **`orders.gross_amount`:** Contains several high-value outlier amounts relative to average item costs. These can skew monetary (RFM) modeling and require robust scaling (Winsorization or Log-transforms) during feature formulation.
* **Negative values:** Validation of `support_tickets.sentiment_score` bounds shows acceptable scaling between `-1` and `1`, but severe negative scores (`-1.0`) act as direct indicators of high churn risks rather than random anomalies.

## 4. Timeline, Temporal Consistency & Target Leakage Rules
* **CRITICAL TARGET LEAKAGE RISK:** `orders.csv` contains transactions extending past the snapshot window (`2025-09-30`) into October and November 2025. 
* **Remediation Rule:** All structural calculations for Part 1 & Part 2 profile creation *must* discard any rows where `order_date > '2025-09-30'`. Post-snapshot orders are strictly reserved for validating the ground truth target labels (`churn_next_60d`) and must never be exposed to your model's feature generation space.
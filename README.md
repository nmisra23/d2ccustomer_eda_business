# Capstone Project: Part 1 — Data Audit, EDA & Business Understanding

## Repository Contents
* `requirements.txt` - Python package environment definitions.
* `eda_audit.ipynb` - End-to-end sandbox performing dataset sanitization, leakage controls, and predictive hypothesis checks.
* `data_quality_report.md` - Technical audit outlining structural constraints, deduplication strategies, and feature isolation rules.
* `business_memo.md` - High-level operational insights translated for marketing and executive CRM planning.

## Verification & Execution Instructions
To execute the exploration pipeline locally without manual configuration paths, run the following commands:

```bash
# 1. Initialize environment setup
pip install -r requirements.txt

# 2. Launch the analysis environment
jupyter notebook eda_audit.ipynb
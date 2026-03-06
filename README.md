# End-to-End Fraud Monitoring & Risk Strategy Pipeline

*A production-style data QA and fraud detection framework focusing on Deliverable Stability, Operational Capacity, and UDAAP Compliance.*

## ⏱️ Quick Proof (30-Second Executive Summary)
- **SQL Controls**: Window functions + point-in-time features engineered to prevent leakage (see `/sql/data_pipeline.sql`).
- **Python Automation**: Automated QA checks, exception report generation, and `try-except` guardrails (see `/src/risk_strategy.py`).
- **Audit-Ready Outputs**: `/outputs/exceptions_sample.csv` and `/outputs/qa_summary_sample.csv`.

## ⚙️ How to Run
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Execute the risk strategy pipeline
python src/risk_strategy.py

## 🚀 1. Strategic Deliverables (What I Delivered)
* **Leakage-safe baseline**: Implemented a strict **time-based split** and engineered velocity/entity features to handle noisy identity coverage.
* **Operations-ready decisioning**: Converted raw model scores into actionable **Block / Review / Allow** policies.
* **Capacity-safe enforcement**: Implemented **rank-based TopK decisioning** to prevent volume inflation from score ties in production.
* **Tail-risk mitigation**: Identified a critical tail anomaly (score $\ge$ 0.95 yielded 0 observed fraud) and implemented a **tail guardrail**.
* **Audit & governance**: Shipped **reason codes** and an **alert playbook** for operational auditability.

## 📊 2. The "Money Chart" (Operating Point Selection)
To translate model performance into business value, I evaluated the financial trade-off under a fixed **manual review capacity of 5,000/day**:
* **Selected Operating Point**: TopK = 5,000.
* **Net Value**: $\approx$ 5,143 (illustrative units).
* **Threshold Ref**: $\approx$ 0.77341.
* **Decision Logic**: Capacity is enforced via rank-based TopK to ensure the operations team is never overwhelmed.

## 📈 3. Key Performance & Validation
* **Model Stability**: Verified score distribution stability with **PSI (train$\rightarrow$valid) $\approx$ 0.0017 (GREEN)**.
* **Risk vs. Friction**: 
    * REVIEW precision $\approx$ **9.5%**.
    * BLOCK/Step-up precision $\approx$ **11%**.
* **Tail Anomaly Evidence**: Transactions with score $\ge$ 0.95 had a **fraud_rate = 0** ($n \approx 1,018$), justifying the mandatory tail guardrail.

## 🛡️ 4. Compliance & UDAAP Strategy
* **Friction Control**: With ~89% false positives in the highest band, "BLOCK" is explicitly treated as **step-up verification** (OTP/2FA/3DS) rather than a hard deny to reduce customer harm and UDAAP risk.
* **Next Steps**: Iterating towards a calibrated GBDT model to improve precision@TopK and reduce the customer insult rate.

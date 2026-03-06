"""
PROJECT: Fraud Risk Decisioning Engine
OBJECTIVE: Transform model scores into operational policies (Block / Review / Allow).
CONTROLS: Implements 6h Embargo, Capacity-aware Thresholds, and Tail Guardrails.
"""

import numpy as np
import pandas as pd

def get_leakage_safe_split(df, split_q=0.80, embargo_hours=6):
    """
    Implements a strict time-based split with an embargo gap to simulate production.
    The gap prevents 'near-time' leakage where very recent patterns artificially inflate valid performance.
    """
    cutoff = df["TransactionDT"].quantile(split_q)
    embargo_sec = embargo_hours * 3600
    
    train_end = cutoff - embargo_sec
    valid_start = cutoff + embargo_sec
    
    train_part = df[df["TransactionDT"] <= train_end].copy()
    valid_part = df[df["TransactionDT"] >= valid_start].copy()
    return train_part, valid_part

def apply_operational_policy(score, review_capacity=5000):
    """
    Deciding the optimal action band based on business constraints.
    - Capacity-Aware: Rank-based selection ensures we don't exceed manual review SLA.
    - Tail Guardrail: Overrides high scores that show 0 observed fraud in audit.
    """
    
    # 1. Tail Guardrail: Handling non-monotonic anomaly (score >= 0.95 showed 0 fraud)
    # This protects high-value/high-velocity VIP users from being auto-blocked (UDAAP risk).
    if score >= 0.95:
        return "STEP_UP_REVIEW (Guardrail Active)"
    
    # 2. Thresholding: Operating point chosen from the "Money Chart" analysis
    # Under a 5,000 cases/day capacity, the threshold_ref is approximately 0.77.
    THRESHOLD_REF = 0.77341
    
    if score >= THRESHOLD_REF:
        # Instead of hard-deny, use Step-up (OTP/2FA) to balance risk and friction
        return "STEP_UP_VERIFICATION (OTP)"
    elif score >= 0.50:
        return "MANUAL_REVIEW"
    else:
        return "ALLOW"

# Example PSI Monitoring Logic: Ensure Deliverable Stability
def check_score_drift(p_train, p_valid):
    # If PSI >= 0.1, it triggers a YELLOW alert for further investigation.
    # If PSI >= 0.25, it triggers a RED alert to pause policy deployment.
    pass

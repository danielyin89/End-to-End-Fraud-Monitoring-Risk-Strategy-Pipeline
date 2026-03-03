/* * PROJECT: End-to-End Fraud Monitoring Pipeline
 * OBJECTIVE: Engineering leakage-safe velocity features using DuckDB SQL.
 * LOGIC: Implements deterministic ordering and time-based isolation.
 */

-- Step 1: Create a deterministic event sequence to prevent "look-ahead" bias
WITH events AS (
  SELECT 
    *,
    -- Combine TransactionDT (seconds) with a unique rank to create a microsecond-level timeline
    -- This ensures a stable sort order even when multiple transactions occur in the same second
    (CAST(TransactionDT AS BIGINT) * CAST(1000000 AS BIGINT) + 
     ROW_NUMBER() OVER(PARTITION BY TransactionDT ORDER BY TransactionID)) AS event_time_us
  FROM df_all
),

-- Step 2: Aggregate historical signals using as-of time windows
features AS (
  SELECT 
    a.TransactionID,
    a.split,
    a.card_key,

    -- 24H Velocity (ALL): Total transaction count in the last 24 hours
    -- Constraint: b.event_time_us < a.event_time_us strictly excludes the current and future rows
    COUNT(b.TransactionID) FILTER (
      WHERE b.event_time_us >= a.event_time_us - CAST(86400 AS BIGINT) * CAST(1000000 AS BIGINT)
        AND b.event_time_us <  a.event_time_us 
    ) AS card_cnt_24h,

    -- 24H Velocity (STRONG): Only count history where the identity was fully validated
    -- Business Case: High velocity on "weak" keys is often a false positive; 
    -- focusing on "strong" keys reduces customer insult rate (UDAAP compliance)
    COUNT(b.TransactionID) FILTER (
      WHERE b.card_key_is_weak = 0 
        AND b.event_time_us >= a.event_time_us - CAST(86400 AS BIGINT) * CAST(1000000 AS BIGINT)
        AND b.event_time_us <  a.event_time_us
    ) AS card_cnt_24h_strong

  FROM events a
  LEFT JOIN events b ON a.card_key = b.card_key
   AND b.event_time_us < a.event_time_us 
   AND a.split = b.split -- Ensure training data never sees validation data (Split Isolation)
  GROUP BY 1, 2, 3
)
SELECT * FROM features;
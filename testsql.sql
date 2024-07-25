CREATE TEMP VIEW transaction_dates AS
SELECT
    shop_id,
    date,
    LAG(date) OVER (PARTITION BY shop_id ORDER BY date) AS prev_date,
    n_trans
FROM transactions;

CREATE TEMP VIEW status_intervals AS
SELECT
    shop_id,
    CASE
        WHEN prev_date IS NULL THEN date  
        WHEN JULIANDAY(date) - JULIANDAY(prev_date) > 30 THEN DATE(prev_date, '+1 day') 
        ELSE date
    END AS status_start,
    CASE
        WHEN prev_date IS NULL THEN 'open' 
        WHEN JULIANDAY(date) - JULIANDAY(prev_date) > 30 THEN 'closed'
        ELSE 'open'
    END AS status,
    CASE
        WHEN prev_date IS NULL THEN 0 
        WHEN JULIANDAY(date) - JULIANDAY(prev_date) > 30 THEN 1
        ELSE 0
    END AS status_change
FROM transaction_dates;


CREATE TEMP VIEW status_ranges AS
SELECT
    shop_id,
    status,
    status_start,
    LEAD(status_start, 1) OVER (PARTITION BY shop_id ORDER BY status_start) AS next_status_start,
    SUM(status_change) OVER (PARTITION BY shop_id ORDER BY status_start) AS change_group
FROM status_intervals;

CREATE TEMP VIEW final_ranges AS
SELECT
    shop_id,
    status,
    MIN(status_start) AS lower_range,
    MAX(next_status_start) AS upper_range,
    change_group
FROM status_ranges
GROUP BY shop_id, status, change_group;

SELECT
    shop_id,
    status,
    lower_range,
    CASE
        WHEN upper_range IS NULL THEN NULL
        ELSE DATE(upper_range, '-1 day')
    END AS upper_range
FROM final_ranges
WHERE NOT (status = 'closed' AND lower_range = upper_range)
ORDER BY shop_id, lower_range;

import sqlite3

def create_status_view(db_name='outlets_transactions.db'):
    """Create a view to show the open/closed status of outlets over time."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    create_view_query = """
    CREATE VIEW IF NOT EXISTS outlet_status AS
    WITH transaction_dates AS (
        SELECT
            shop_id,
            date,
            LAG(date) OVER (PARTITION BY shop_id ORDER BY date) AS prev_date,
            n_trans
        FROM transactions
    ),
    status_intervals AS (
        SELECT
            shop_id,
            CASE
                WHEN prev_date IS NULL THEN date  -- 初始状态为 open，从当前日期开始
                WHEN JULIANDAY(date) - JULIANDAY(prev_date) > 30 THEN DATE(prev_date, '+1 day')  -- closed 从前一天的下一天开始
                ELSE date
            END AS status_start,
            CASE
                WHEN prev_date IS NULL THEN 'open'  -- 初始状态为 open
                WHEN JULIANDAY(date) - JULIANDAY(prev_date) > 30 THEN 'closed'
                ELSE 'open'
            END AS status,
            CASE
                WHEN prev_date IS NULL THEN 0  -- 初始状态不计为变化
                WHEN JULIANDAY(date) - JULIANDAY(prev_date) > 30 THEN 1
                ELSE 0
            END AS status_change
        FROM transaction_dates
    ),
    status_ranges AS (
        SELECT
            shop_id,
            status,
            status_start,
            LEAD(status_start) OVER (PARTITION BY shop_id ORDER BY status_start) AS next_status_start,
            SUM(status_change) OVER (PARTITION BY shop_id ORDER BY status_start) AS change_group
        FROM status_intervals
    ),
    final_ranges AS (
        SELECT
            shop_id,
            status,
            MIN(status_start) AS lower_range,
            MAX(next_status_start) AS upper_range,
            change_group
        FROM status_ranges
        GROUP BY shop_id, status, change_group
    )
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
    """
    cursor.execute(create_view_query)
    conn.commit()
    conn.close()

 # Execute 
create_status_view()
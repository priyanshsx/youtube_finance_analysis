-- sql scripts used to conduct analysis on duckdb 

-- create tables 
CREATE TABLE main AS SELECT * FROM read_auto_csv('...path/youtube_videos.csv')
CREATE TABLE vix AS SELECT * FROM read_auto_csv('...path/^VIX.csv')
CREATE TABLE gspc AS SELECT * FROM read_auto_csv('...path/^GSPC.csv')


-- checking for NULLs 
SELECT * FROM merged WHERE channel_name IS NULL OR video_id IS NULL OR duration_seconds IS NULL or view_count IS NULL or like_count IS NULL OR comment_count IS NULL 

-- checking for date lags in vix and gspc 
SELECT 
    date,
    LAG(date) OVER (ORDER BY date),
    date - LAG(date) OVER (ORDER BY date) AS day_gap
FROM 
    vix

-- forward-filling the dates for gspc and vix 
    -- creating a date spine 
    CREATE TABLE date_spine AS 
    SELECT CAST(generate_series AS date) AS continuous_date
    FROM generate_series(
        DATE '2023-01-01',
        DATE '2026-09-15',
        INTERVAL '1 DAY'
    )

    -- merging gspc and vix 
    CREATE TABLE gspc_continuous_date AS 
    SELECT * FROM date_spine 
    LEFT JOIN gspc
    ON date_spine.continuous_date = gspc.date

    CREATE TABLE vix_continuous_date AS 
    SELECT * FROM date_spine 
    LEFT JOIN vix
    ON date_spine.continuous_date = vix.date
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

    -- merging date_spine and gspc and vix 
    CREATE TABLE gspc_continuous_date AS 
    SELECT * FROM date_spine 
    LEFT JOIN gspc
    ON date_spine.continuous_date = gspc.date

    CREATE TABLE vix_continuous_date AS 
    SELECT * FROM date_spine 
    LEFT JOIN vix
    ON date_spine.continuous_date = vix.date

CREATE TABLE vix_filled_close AS
SELECT 
    close, high, low, open,
    continuous_date,
    LAST_VALUE(close) IGNORE NULLs OVER (ORDER BY continuous_date 
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS vix_filled_close
FROM vix_continuous_date

CREATE TABLE gspc_filled_close AS
SELECT 
    continuous_date,
    LAST_VALUE(close) IGNORE NULLs OVER (ORDER BY continuous_date 
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS gspc_filled_close
FROM gspc_continuous_date


-- sentiment, sponsorship, and duration check 
CREATE TABLE main_regex AS 
WITH tagged_videos AS (
    SELECT 
        channel_name,
        title, 
        publish_date,
        duration_seconds,
        view_count, 
        like_count,
        comment_count,
        description,
        
        CASE 
            WHEN duration_seconds < 180 THEN 'micro'
            WHEN duration_seconds <= 600 THEN 'short'
            WHEN duration_seconds <= 1200 THEN 'medium'
            ELSE 'long'
        END AS duration_bucket,
        CASE 
            -- fear
            WHEN regexp_matches(title, '(?i)\b(crash|warning|collapse|bubble|crisis|recession|panic|emergency|disaster|doomsday|liquidation|debasement|screwed|trap|chaos|red flag|yikes|speechless|falter)\b|\b(it.?s over|do not buy|don.?t buy|lose everything|falls? apart|rushing for the exits?|much worse|end of the world|f\*\*k.?d)\b') THEN 'fear'
            -- opportunity
            WHEN regexp_matches(title, '(?i)\b(skyrocket|bullish|moon|soar|banger|unbelievable)\b|\b(wealth transfer|generational|bull run|infinite money glitch|make millions|must buy|all in|life.?changing|never get a chance|filthy rich|go nuts|do not sell|don.?t sell|wealth rotation)\b') THEN 'opportunity'
            -- evergreen 
            WHEN regexp_matches(title, '(?i)\b(passive income|roth ira|401k|retire|budget|habits?|mindset|credit score|net worth|taxes|portfolio|salary|guide|milestones?)\b|\b(how to|explains?|buy.* vs .*rent|rent.* vs .*buy|financial plan|saving|debt mistakes?|wealth building|long game|getting rich|quiet quit)\b') THEN 'evergreen'
            -- neutral 
            WHEN regexp_matches(title, '(?i)\b(bitcoin|btc|crypto|altcoin|ai|dropshipping|real estate|mortgage|cpi|inflation|jobs report|fed|vix|gold|silver|wall street)\b') THEN 'neutral'
            ELSE 'undefined'
        END AS title_category,
        CASE 
            -- sponsorship check 
            WHEN regexp_matches(description, '(?i)\b(sponsored by|thanks to.* for sponsoring|paid partnership|ad)\b') THEN TRUE
            ELSE FALSE 
        END AS is_sponsored
        
        FROM main
)

SELECT *, 
    CASE 
        WHEN is_sponsored = TRUE AND regexp_matches(description, '(?i)\b(webull|robinhood|m1 finance|interactive brokers|moomoo|public.com)\b') THEN 'brokerage'
        WHEN is_sponsored = TRUE AND regexp_matches(description, '(?i)\b(coinbase|kraken|ledger|trezor|binance|metamask)\b') THEN 'crypto wallets'
        WHEN is_sponsored = TRUE AND regexp_matches(description, '(?i)\b(turbotax|taxact|inc .* authority|rocket lawyer|quickbooks)\b') THEN 'tax software'
        WHEN is_sponsored = TRUE AND regexp_matches(description, '(?i)\b(nordvpn|tradingview|trading view|expressvpn|surfshark|incogni|deleteme|audible)\b') THEN 'tech/privacy'
        WHEN is_sponsored = TRUE THEN 'other sponsor'
        ELSE 'organic'
    END AS sponsor_category
FROM tagged_videos

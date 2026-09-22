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

-- new columns to add: 
-- title_sentiment: fear, evergreen, opportunity, other  
    -- word categories: 
    -- fear: market crash, bitcoin crash, btc crash, crashing soon, you need to see this, 
        -- warning, now is the time, its coming, it's coming, ai bubble, collapse, insane, 
        -- debt, mortgage, flaws, flawed, collapsing, massive bailout, bailout, reset, 
        -- reset the market, crisis, crash the economy, economy crashing, do not buy,  
        -- don't buy, dont buy, erasing, erase,  STOP, repression, financial repression, 
        -- end of the world, be prepared, preparing, tariff war, financial crisis, energy crisis, 
        -- explode, exploding, explodes, explosion, its over, it's over, it is over, fraud, breaking, 
        -- break, broken, america buying debt, japan buying america's debt, fell, stock market fell, 
        -- skyrocket, skyrocketing, recession, f**k'd, SEC bailout, sec, peak fear, fear, 
        -- vix, speechless, critical bubble, critical, yikes, red flag, end of, about to flip, flip, 
        -- exposed the collapse, crushed, attack, strikes, strikes on iran, strike iran, nuclear strike, 
        -- horrible, problem, concern, liquidated, liquidation, breakdown, falter, faltering, flippening,
        -- hidden debt, falls apart, fall apart, rushing for the exit, rushing for the exits, debasement, 
        -- debasement trade, trade war, doomsday, doomsday cult, lose everything, money loser, loser,
        -- epstein, bitcoin crash, btc crash, crypto market, crypto crash, dollar is losing value, altcoin,
        -- crushes expectations, yen crisis, jobs report, disaster, cpi, inflation, much worse, 
        -- 
          

    -- evergreen: make money with ai, make money, passive income ideas, passive income, 
        -- dropshipping, wants to get rich, want to get rich, i f**kd up, f**kd up, china, 
        -- ai race, mortgage, Roth IRAs, tax cuts, us economy, 401k, money mindset, mindset, escape, 
        -- retire wealthy, retire, retirement, $1,000, $10,000, $1000, $10000, screwed, are we screwed,
        -- vacation, vacations, overspend, trap, car payment, mortgage trap, car payment trap, calm, 
        -- calm about money, not normal, build wealth, are we screwed, is it over for us, rules for travel, 
        -- rules for investing, rules for markets, aging parents, prepare, $0 to $10K, $0 to $100k, 
        -- 0 to 10k, 0 to 100k, can't pay, cant pay, cannot pay, cant stop spending, can't stop spending, 
        -- debt mistakes, keep you broke, financial freedom, freedom from debt, getting rich, 
        -- secretly wealthy, ex-banker, 99% ahead, 99% financially ahead, quiet quit, 
        -- quiet quitting, quietly quitting, $__k rule, nobody tells you this, below $100K, net worth, 
        -- buy these, buy these asap, buying vs renting, buying versus renting, never finance, finance a car, 
        -- finance a house, stop buying, daily habits, getting rich, getting wealth, fake rich, 
        -- ultimate playbook, playbook, middle class, conundrum, promotions, what, how, why, what why how, 
        -- rest in peace, thanks, thanks a ton, financial chaos, grow wealth, go slow, financial reality, long game, 
        -- expand your options, keep moving, moving, feelings, facts, bad money habits, financial plan, 
        -- financial plans, financial hardship, slowly, moving slowly, financial decision, myth, happier, 
        -- happy, happiness, was i wrong, i was wrong, i was right, renting vs. buying, renting vs buying, 
        -- wall street, afford, private equity, ai slop, internet, portfolio, borrow against, invest your money, 
        -- money moves, retirement, salary, two incomes, 2 incomes, price prediction, credit score, financial advice, 
        -- prediction markets, tax breaks, online shopping, budget tips, budget tricks, inherit, 
        -- measure the economy, measure, money printer, money printing machine, home prices, mortgage rates, 
        -- 


    -- opportunity: filthy rich during a recession, do not sell, don't sell, go nuts, buy a home,
        -- buying a home, wealth rotation, wealth, wealth accumulation, accumulate, new world order, 
        -- investment opportunity, opportunity, investment, invest, investment returns, investment return, 
        -- quit your job, accountant explains, accountant, saving $100K, most people get this wrong, 
        -- how i invest, how to invest, good things, good things for you, good things happen, good things happen to you, 
        -- if i wanted to become a millionaire, wanted to become a millionaire, net worth milestones, 
        -- grow your net worth, grow your worth, know your worth, know your net worth, skyrocket, memestocks, 
        -- top, bottom, market top, market bottom, oil money, infinite money glitch, money glitch,  
        -- generational opportunity, wealth transfer, generational, once in a generation, bull run, crypto strategy, 
        -- make millions, make thousands, gameplan, strategy, bullish, investing in, invest in gold, invest in silver, 
        -- gold, silver, all in, soar, started, begun, beginning, rich, load, life-changing, life changing, 
        -- unbelievable, never get a chance like this, greatest stock ever, greatest crypto ever, greatest coin ever, 
        -- banger, growth, must buy, ultra high growth, fly, 




-- title_theme: trading_ed, investing_ed, economic_ed, business_ed, ai_ed, tech_ed, life_ed,
-- is_sponsored: yes/no, 
-- sponsor_type (Brokerage, VPN, trading software, other), 
-- duration_bucket (short: <10, medium: 10-20, long: 20+)


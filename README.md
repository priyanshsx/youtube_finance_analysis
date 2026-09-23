# Finance YouTube: What dominates? Fear or frugality? 

An empirical study decoding algorithmic performance, creator resilience, and audience fatigue across macroeconomic market cycles.

![](/assets/dashboard1_hero_overview.png)


## Executive Overview 

When the stock market panics, financial media shifts instantly—but does fear content actually outperform evergreen financial literacy in raw views and engagement?

This project analyzes the publishing patterns and performance metrics of 17 major financial YouTube creators from January 1, 2023, through September 2026. By linking video performance data against macroeconomic volatility (VIX Index) and market benchmarks (S&P 500), this study models audience fatigue, volatility multipliers, and optimal publishing windows.

## Interactive Dashboards

- [Dashboard 1: Competitor Matrix (17 Creators)](https://public.tableau.com/views/FinanceYouTubeCreatorsCompetitorMatrix17Creators/Dashboard1?:language=en-GB&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

- [Dashboard 2: Winning on Finance YouTube](https://public.tableau.com/views/WinningonFinanceYouTube3ChartsYouNeedtoSee/Dashboard1?:language=en-GB&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Eligibility Criteria 
Any YouTube content creator that regularly publishes finance, investment (equities, commodities, crypto, real estate) related content as their primary content creation and has been publishing regularly since January 1st, 2023 until September 2026, have a subscriber count of at least 650k. 

The following candidates were chosen for this analysis. An exception has been made for Ben Felix (641K subscribers < threshold subscribers count). 

1. Mark Tilbury
2. Graham Stephen
3. Andrei Jikh
4. Minority Mindset
5. I Will Teach You To Be Rich
6. Nicha
7. Humprhey Yang
8. Meet Kevin
09. The Plain Bagel
10. The Ramsey Show 
11. Ben Felix 
12. Patrick Boyle 
13. Marko - WhiteBoard Finance 
14. Two Cents PBS  
15. Brian Jung
16. ClearValue Tax
17. Financial Education

NB: All Live/Broadcast videos were skipped from this analysis. 

## Core Research Questions

1. **Macro Performance Gap**: Does high market volatility ($VIX > 20$) widen the performance gap between "Fear" titles and "Evergreen" literacy titles by at least 50%?
2. **Optimal Video Duration**: Does the 10–20 minute video duration window achieve the optimal balance for reach and engagement across market regimes?
3. **Pivot Reaction Time**: How many days does it take for individual creators to pivot toward panic/fear content following a major VIX spike or S&P 500 selloff?
4. **Fear Fatigue Threshold**: Is there a diminishing returns threshold where repeatedly publishing "market crash" or "recession" titles leads to engagement collapse?
5. **Volatility Multipliers**: Which creators capture the highest view multipliers when market volatility surges? 
6. **Urgency Premium**: Do high-urgency keywords ("Warning", "Do THIS", "Emergency", "Before it's too late") achieve measurable view velocity and engagement lifts over factual titles?

## Findings 

### Macro Market Dynamics & Content Strategy 

- **Performance Gap**: High volatility does not widen the performance gap between "Fear" and "Evergreen" content. Instead, median daily views drop severely for both categories during a VIX spike. In a normal market, fear content averages roughtly 1,898 views versus evergreen's 1022. During a volatile market, both crash proportionally to 776 views and 422 views, respectively. 

- **Urgency Keywords (Question 7)**: Titles utilizing high-urgency keywords ("warning", "alert", etc.) definitively outperform standard factual titles. Urgent titles capture a median view velocity of 1,449 (vs. 1,134 for standard) and achieve a higher median engagement rate of 3.43% (vs. 2.99%).

### 1. Video Format and Duration 

- **Reach vs. Engagement Trade-off**: The 10-20 minute "Medium" duration is not the optimal balance. Long-form content (>20 minutes) dominates raw reach across all markets, pulling 2,030 daily views in normal conditions and 1,041 in volatile conditions. Conversely, short-form content (3-10 minutes) yields the lowest views but drives the highest engagement rates across both normal (4.13%) and volatile (4.70%) markets.

- **Volatility Boosts Engagement**: While raw viewership drops during high-VIX periods, audience engagement rates actually increase across every single duration bucket during volatile markets.

### 2. Audience Fatique and Diminishing Returns 

- **Engagement Peak and Drop-off**: When creators post consecutive "fear" videos during a prolonged crash, audience engagement rates climb initially, peaking at 5.67% on the 3rd consecutive video in the sequence. However, engagement suffers a steep decline to 3.17% by the 4th consecutive video, indicating audience fatigue.

- **View Velocity Volatility**: The algorithm treats consecutive fear videos erratically. Median views climb to 1,404 on the 2nd video, completely collapse to 95 views on the 3rd, and surge to over 4,297 on the 4th.

### 3. Creator Reaction and Multipliers 

- **The Volatility Multipliers**: While macro viewership drops during a crash, 8 of the creators actively gain viewership. Andrei Jikh (6.76x) and Ben Felix (5.03x) experience massive view multipliers, while channels like Financial Education (0.33x) and Mark Tilbury (0.50x) lose more than half their baseline audience.
- **Reaction Time**: Several financial creators, including Graham Stephan, ClearValue Tax, and Patrick Boyle, execute a 0-day pivot, pushing panic content immediately upon a regime shift. More measured channels like Two Cents (7 days) and The Plain Bagel (25.5 days) significantly lag the market reaction.

## Technical Stack & Execution Pipeline

1. SQL & Data Engineering (DuckDB): Ingested, cleaned, and structured row-level video data, S&P 500 index movements, and historical VIX levels.
2. Quantitative Analysis (Python / Pandas):
    - Gaps & Islands Algorithm: Grouped consecutive market regimes into unique event IDs (regime_shift_id) using .cumsum() vector shifts to isolate discrete volatility cycles.
    - Regex Keyword Extraction: Extracted title urgency using vectorized regex regex patterns (\b(?:warning|alert|critical|do this)\b).
    - Sequence Tracking: Computed consecutive fear upload counts (fear_sequence) per channel per volatility island using .cumcount().
3. Data Visualization (Tableau Desktop): Constructed dual-axis performance models, scatter plot quadrant analyses, and strategic playbook dashboards.
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from scipy import stats 
import statsmodels.api as sm 
import duckdb 

# importing the master table 

con = duckdb.connect('/home/priyansh/Documents/d/youtube_finance_analysis/db/main.duckdb')

df = con.sql("SELECT * FROM master").df()

df['publish_date'] = pd.to_datetime(df['publish_date'])

# answering question #1 (refer README)

df_hyp1 = con.sql("""
    SELECT * FROM master WHERE title_category IN ('fear','evergreen')
""").df()

df_hyp1['market_regime'] = np.where(df_hyp1['vix_close']  > 20, 'Volatile', 'Normal')

q1_df = df_hyp1.groupby(['market_regime', 'title_category'])['view_velocity'].median().unstack()

# answering question #2 (refer README)

df['market_regime'] = np.where(df['vix_close'] > 20, 'Volatile', 'Normal')

q2_vv = df.groupby(['market_regime', 'duration_bucket'])['view_velocity'].median().unstack()
q2_er = df.groupby(['market_regime', 'duration_bucket'])['engagement_rate'].median().unstack()

# answering question #7 (refer README)

urgency_keywords = '(?i)\\b(?:warning|do this|emergency|before it.?s too late|alert|critical|now)\\b'
df['urgency_keywords'] = np.where(df['title'].str.contains(urgency_keywords, regex=True, case=False, na=False), 'Urgent', 'Standard')

q7_vv = df.groupby('urgency_keywords')['view_velocity'].median()
q7_er = df.groupby('urgency_keywords')['engagement_rate'].median()

# answering question #4 (refer README)

df = df.sort_values(['channel_name', 'publish_date'])

df['regime_shift_id'] = (df['market_regime'] != df['market_regime'].shift(1)).cumsum()

q4_filter = df[(df['market_regime'] == 'Volatile') & (df['title_category'] == 'fear')].copy()

q4_filter = q4_filter.sort_values(['channel_name', 'publish_date'])

q4_filter['fear_sequence'] = q4_filter.groupby(['channel_name', 'regime_shift_id']).cumcount() + 1

q4_vv = q4_filter.groupby('fear_sequence')['view_velocity'].median().head(5)
q4_er = q4_filter.groupby('fear_sequence')['engagement_rate'].median().head(5)

# answering question #5 (refer README)

q5 = df.groupby(['channel_name', 'market_regime'])['view_velocity'].median().unstack()

q5['view_multiplier'] = q5['Volatile'] / q5['Normal']

q5_ranked = q5.sort_values('view_multiplier', ascending=False)

# answering question #3 (refer README)

# isoloating just the volatile market regime

volatile_df = df[df['market_regime'] == 'Volatile'].copy()

# finding the start date of every volatile period 

vol_starts = volatile_df.groupby('regime_shift_id')['publish_date'].min().reset_index()
vol_starts.rename(columns={'publish_date': 'island_start_date'}, inplace=True)

# first video by the creator during that regime shift to volatile (we'll be looking at fear videos only)
fear_df = volatile_df[volatile_df['title_category'] == 'fear']
first_fear_video = fear_df.groupby(['regime_shift_id', 'channel_name'])['publish_date'].min().reset_index()
first_fear_video.rename(columns={'publish_date': 'first_fear_video_date'}, inplace=True)

# merging the two dataframes
pivot_df = pd.merge(first_fear_video, vol_starts, on='regime_shift_id')

# calculating the days difference 
pivot_df['days_to_pivot'] = (pivot_df['first_fear_video_date'] - pivot_df['island_start_date']).dt.days

# calculating the final no. of days it takes for a creator to pivot to making fear videos
q3_final = pivot_df.groupby('channel_name')['days_to_pivot'].median().sort_values()

# printing values 

print("---" * 30)
print("\nPerformance Gap between Fear and Evergreen titles:")
print(q1_df)
print("Video Duration & View Velocity:")
print(q2_vv)
print("\nVideo Duration & Engagement Rate:")
print(q2_er)
print("\nMedian Views by Urgency Level:")
print(q7_vv)
print("\nEngagement Rate by Urgency Level:")
print(q7_er)
print("\nDiminishing returns per fear videos (Engagement Rate):")
print(q4_er)
print("\nDiminishing returns per fear videos (View Velocity):")
print(q4_vv)
print("\nView Multiplier by Creator (Volatile / Normal)):")
print(q5_ranked[['Normal', 'Volatile', 'view_multiplier']])
print("\nNo. of days it takes a creator to pivot to making 'fear' videos:")
print(q3_final)
print("---" * 30)
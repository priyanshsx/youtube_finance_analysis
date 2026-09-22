import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from scipy import stats 
import statsmodels.api as sm 
import duckdb 

# importing the master table 

con = duckdb.connect('/home/priyansh/Documents/d/youtube_finance_analysis/db/main.duckdb')

df = con.sql("SELECT * FROM master").df()

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

urgency_keywords = '(?i)\\b(warning|do this|emergency|before it.?s too late|alert|critical|now)\\b'
df['urgency_keywords'] = np.where(df['title'].str.contains(urgency_keywords, regex=True, na=False), 'Urgent', 'Standard')

q7_vv = df.groupby('urgency_level')['view_velocity'].median()
q7_er = df.groupby('urgency_level')['engagement_rate'].median()

# answering question #4 (refer README)


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
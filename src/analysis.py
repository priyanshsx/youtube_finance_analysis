import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from scipy import stats 
import statsmodels.api as sm 
import duckdb 

# importing the master table 

con = duckdb.connect('/home/priyansh/Documents/d/youtube_finance_analysis/db/main.duckdb')

df = con.sql("SELECT * FROM master").df()

# hypothesis testing: #1 (refer README)

df_hyp1 = con.sql("""
    SELECT * FROM master WHERE title_category IN ('fear','evergreen')
""").df()

df_hyp1['market_regime'] = np.where(df_hyp1['vix_close']  > 20, 'Volatile', 'Normal')

filtered_df = df_hyp1.groupby(['market_regime', 'title_category'])['view_velocity'].median().unstack()
# print(filtered_df)

# hypothesis testing: #3 (refer README)

df['market_regime'] = np.where(df['vix_close'] > 20, 'Volatile', 'Normal')

hyp3_vv = df.groupby(['market_regime', 'duration_bucket'])['view_velocity'].median().unstack()
hyp3_er = df.groupby(['market_regime', 'duration_bucket'])['engagement_rate'].median().unstack()
print("Hypothesis 3 - View Velocity:")
print(hyp3_vv)
print("\nHypothesis 3 - Engagement Rate:")
print(hyp3_er)
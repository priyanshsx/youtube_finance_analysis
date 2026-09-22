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
print(filtered_df)

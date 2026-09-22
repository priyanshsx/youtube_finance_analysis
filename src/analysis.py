import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from scipy import stats 
import statsmodels.api as sm 
import duckdb 

con = duckdb.connect('/home/priyansh/Documents/d/youtube_finance_analysis/db/main.duckdb')

df = con.sql("SELECT * FROM master").df()

print(df.info())
# this checks for words that constantly appear in the youtube video titles to better structure the regex script

import re 
from collections import Counter
import duckdb 

con = duckdb.connect('/home/priyansh/Documents/d/youtube_finance_analysis/db/main.duckdb')

df = con.sql("SELECT title FROM main_regex_check WHERE title_category = 'undefined'").df()

stop_words = {
    'the', 'to', 'and', 'a', 'in', 'is', 'it', 'you', 'of', 'for', 'on', 'my', 
    'this', 'what', 'i', 'why', 'are', 'how', 'with', 'at', 'we', 'be', 'do', 
    'that', 'your', 'from', 'up', 'out', 'not', 'as', 'about', 'can', 'will', 'if'
}

all_words = []
for title in df['title']:
    words = re.findall(r'\b[a-z0-9]+\b', str(title).lower())
    all_words.extend([word for word in words if word not in stop_words])

word_counts = Counter(all_words)
for word, count in word_counts.most_common(50):
    print(f"{word}: {count}")
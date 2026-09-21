-- sql scripts used to conduct analysis on duckdb 

-- create table 
CREATE TABLE main AS SELECT * FROM read_auto_csv('...path/youtube_videos.csv')


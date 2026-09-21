-- sql scripts used to conduct analysis on duckdb 

-- create table 
CREATE TABLE main AS SELECT * FROM read_auto_csv('...path/youtube_videos.csv')

-- checking for NULLs 
SELECT * FROM merged WHERE channel_name IS NULL OR video_id IS NULL OR duration_seconds IS NULL or view_count IS NULL or like_count IS NULL OR comment_count IS NULL 


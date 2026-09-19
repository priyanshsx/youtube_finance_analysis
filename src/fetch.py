import os 
import re 
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build

# extracts the API key from the .env file 

load_dotenv()
API_KEY = os.environ.get('YOUTUBE_API_KEY')

if not API_KEY:
    raise RuntimeError(
        'YOUTUBE_API_KEY is not set. Add it to the project-root .env file or export it before running this script.'
    )

youtube = build('youtube', 'v3', developerKey=API_KEY)

# channel IDs
# 1) anthony pompliano 
# 2) the moon show 
# 3) moneyzg
# 4) cryptosrus
# 5) virtualbacon
# 6) benjamin cowen
# 7) cryptobanter
# 8) discover crypto 
# 9) altcoin daily
# 10) coinbureau

# adding the channel IDs

CHANNEL_IDS = [
    'UCML9PlpcOxM_H53IM0fa4XA',
    'UCc4Rz_T9Sb1w5rqqo9pL1Og',
    'UCIEvlRpHBVFthrF6pZzBEXw',
    'UCI7M65p3A-D3P4v5qW8POxQ',
    'UCcrEA_xd9Ldf1C8DIJYdyyA',
    'UCRvqjQPSeaWn-uEx-w0XOIg',
    'UCN9Nj4tjXbVTLYWN0EKly_Q',
    'UCjemQfjaXAzA-95RKoy9n_g',
    'UCbLhGKVY-bJPcawebgtNfbw',
    'UCqK_GSMbpiV8spgD3ZGloSw'
] 

VIDEOS_PER_CHANNEL = 50

# building the get videos function 

def get_video_ids(channel_id, max_results=50):
    # Convert channel ID to its uploads playlist ID (UC -> UU)
    uploads_playlist_id = 'UU' + channel_id[2:]

    video_ids = []
    next_page_token = None

    while len(video_ids) < max_results:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=min(50, max_results - len(video_ids)),
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

# parser function to help convert the youtube-reported time of  ISO 8601 to seconds
# self-disclosure: took claude's help to write this bit as it wasn't something i had studied previously 
 
def parse_duration(iso_duration):

    # ensuring that only those digits are captured which are present as all videos may not be hour-long

    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)

    # extracting just the numbers from each group 

    hours = int(match.group(1)) if match.group(1) else 0 
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    # computing everything into seconds 
    return hours * 3600 + minutes * 60 + seconds

# now we need to extract 50 videos from each channel 
# created a function that helps pull title, views, likes, comments, and duration 
# we batch the videos in groups of 50s because youtube's videos.list allows up to 50 video IDs per single API call 

def get_video_details(video_ids, channel_name):
    all_rows = [] # for storing one dict per video 

    for i in range(0, len(video_ids), 50):
        # grabbing 50 videos starting at index i
        batch = video_ids[i:i+50]

        request = youtube.videos().list(
            # snippet: title/date, statistics: likes/views/comments, contentdetails: duration
            part='snippet,statistics,contentDetails',
            id = ','.join(batch)
        )

        response = request.execute()

        # self-disclosure: took claude's help for indexing video details 
        for item in response['items']:
            all_rows.append({
                'channel_name': channel_name,
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'publish_date': item['snippet']['publishedAt'],
                'duration_seconds': parse_duration(item['contentDetails']['duration']),
                'view_count': int(item['statistics'].get('viewCount', 0)), # adding 0 if view count not available 
                'like_count': int(item['statistics'].get('likeCount', 0)), # same as above
                'comment_count': int(item['statistics'].get('commentCount', 0)) # same as above
            })
    return all_rows

# defining the main function that 
# loops over 1) every channel in CHANNEL_IDS, pulls its videos in batches, and 
# combines everything into one final .csv file 

def main(): 
    all_data = [] # accumulates every video from every channel into this 

    # self-disclosure: took claude's help for converting the channel_id into channel_name
    for channel_id in CHANNEL_IDS: 
        channel_response = youtube.channels().list(part='snippet', id=channel_id).execute()
        channel_name = channel_response['items'][0]['snippet']['title']

        # added a little progress tracker while the function runs 
        print(f"Fetching for {channel_name}")     

        # for the given channel, get its last 50 video ids
        video_ids = get_video_ids(channel_id, max_results=VIDEOS_PER_CHANNEL)

        # get full details for those specific video ids
        video_data = get_video_details(video_ids, channel_name)

        all_data.extend(video_data)

    # converting the list of dicts into a proper table
    df = pd.DataFrame(all_data)

    os.makedirs('raw_data', exist_ok=True)
    df.to_csv('raw_data/youtube_videos.csv', index=False)
    print(f"Saved {len(df)} rows to youtube_videos.csv")


if __name__ == '__main__':
    main()
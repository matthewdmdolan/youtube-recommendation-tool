# import requests
from datetime import datetime, timedelta
import pandas as pd
from apiclient.discovery import build
import json
from cfg import api_key
import plotly.express as px
import sweetviz as sv

# API parameters
api_key = api_key
start_time = datetime(year=2022, month=7, day=12).strftime('%Y-%m-%dT%H:%M:%SZ')
end_time = datetime(year=2023, month=7, day=12).strftime('%Y-%m-%dT%H:%M:%SZ')
youtube = build('youtube', 'v3', developerKey=api_key)

# calling api
video_information_json = youtube.search().list(q="Disco Music", part="snippet", type="video", order="viewCount",
                                               publishedAfter=start_time,
                                               publishedBefore=end_time, maxResults=500).execute()

# Create a pretty print output to establish a better view of the structure
with open('results.json', 'w') as f:
    json.dump(video_information_json, f, indent=10)

# loops through json to extract fields defined below
extracted_fields_video_information = [
    {
        'id': item['id']['videoId'],
        'title': item['snippet']['title'],
        'description': item['snippet']['description'],
        'publishdate': item['snippet']['publishedAt']
    }
    for item in video_information_json['items']
]

# Create the DataFrame from the extracted data
df_video_information = pd.DataFrame(extracted_fields_video_information)
print(df_video_information)

# List of ids to search for
ids_for_statistic = list(df_video_information['id'])

# Create another request to get video statistics using id and merge
video_statistics_json = youtube.videos().list(id=ids_for_statistic, part="statistics", maxResults=500).execute()

# Create a pretty print output to establish a better view of the structure
with open('video_statistics.json', 'w') as f:
    json.dump(video_statistics_json, f, indent=10)
print(video_statistics_json)

# Loops through json to extract fields defined below
extracted_fields_video_statistics = [
    {
        'id': item['id'],
        'viewcount': item['statistics'].get('viewCount'),
        'likes': item['statistics'].get('likeCount'),
        'favourites': item['statistics'].get('favoriteCount'),
        'comments': item['statistics'].get('commentCount')
    }
    for item in video_statistics_json['items']
]

# Create another request to get video statistics using id and merge
df_video_statistics = pd.DataFrame(extracted_fields_video_statistics)
print(df_video_statistics)

# Merging dfs
df_video_combined = df_video_information.merge(df_video_statistics, how='left', on='id')
print(df_video_combined.columns)
print(df_video_combined)

"""Building, plotting and evaluating KPIs"""
def plot_kpi(df, column, title):
    # Sort dataframe by the column to plot
    df_sorted = df.sort_values(column, ascending=False)

    # Create a bar plot for Top 20 videos according to kpi score
    fig = px.bar(df_sorted[:20],
                 x='title',
                 y=column,
                 title=title,
                 labels={column: title, 'title': 'Video Title'},
                 width=800, height=400)

    # Rotate x-axis labels for readability
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

# Changing datatypes for later kpi build
df_video_combined['likes'] = pd.to_numeric(df_video_combined['likes'])
df_video_combined['comments'] = pd.to_numeric(df_video_combined['comments'])
df_video_combined['viewcount'] = pd.to_numeric(df_video_combined['viewcount'])

# Calculating time video has been published for later kpi build
df_video_combined['publishdate'] = pd.to_datetime(df_video_combined['publishdate']).dt.date
df_video_combined['days_since_published'] = (pd.Timestamp.today().date() - df_video_combined['publishdate']).dt.days
print(df_video_combined.columns)

# Calculating views per day
df_video_combined['views_per_day'] = df_video_combined['viewcount'] / df_video_combined['days_since_published']
plot_kpi(df_video_combined, 'views_per_day', 'Top 20 Videos by views_per_day')

# Calculating engagement rate
df_video_combined['engagement_rate'] = (df_video_combined['likes'] + df_video_combined['comments']) / df_video_combined[
    'viewcount']
plot_kpi(df_video_combined, 'engagement_rate', 'Top 20 Videos by Enagement Count')

# Calculating engagement per day - likes and comments
df_video_combined['engagement_per_day'] = (df_video_combined['likes'] + df_video_combined['comments']) / \
                                          df_video_combined['days_since_published']
plot_kpi(df_video_combined, 'engagement_per_day', 'Top 20 Videos by engagement_per_day')

# First iteration of kpi metric with weights
weights = {'views': 0.5, 'likes': 0.3, 'favourites': 0.1, 'comments': 0.1}
df_video_combined['performance_kpi'] = weights['views'] * df_video_combined['viewcount'] + weights['likes'] * \
                                       df_video_combined['likes'] + weights['favourites'] * df_video_combined[
                                           'favourites'] + weights['comments'] * df_video_combined['comments']
plot_kpi(df_video_combined, 'performance_kpi', 'Top 20 Videos by engagement_per_day')

# Getting view of df now all round 1 kpis have been created
report = sv.analyze(df_video_combined)
report.show_html()

"""Accounting for virality"""
# Producing a viral score?
df_video_combined['viral_score'] = df_video_combined['viewcount'] * df_video_combined['engagement_rate']

# Use a weighted moving average: A simple moving average might smooth out the "viral" peaks of a video too much.
# A weighted moving average, which assigns more importance to recent days, might be more appropriate.
# In Python, you could use pandas' ewm (Exponential Weighted Moving) function to calculate this over 7 days:
df_video_combined['views_per_day_weighted_mavg'] = df_video_combined['views_per_day'].ewm(span=7).mean()

# Use a decay factor: Instead of dividing the total views by the number of days since published, you could apply a
# decay factor that reduces the contribution of older views. This could be done in many ways, but one possibility is
# to use an exponential decay
decay_rate = 0.95  # Adjust this as needed
df_video_combined['days_since_published_decay'] = decay_rate ** df_video_combined['days_since_published']
df_video_combined['views_decay_adjusted'] = df_video_combined['viewcount'] / df_video_combined[
    'days_since_published_decay']

"""looking at performance of a mix from a popular channel I know I enjoy and how the metrics perform
--reptitive building api calls so moved to an OOP logic """


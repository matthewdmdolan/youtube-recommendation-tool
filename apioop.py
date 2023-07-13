import pandas as pd
import plotly.express as px
from apiclient.discovery import build
import cfg

class YouTubeAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def video_information(self, query, start_time, end_time, video_id=None):
        if video_id is not None:
            video_information_json = self.youtube.videos().list(
                id=video_id,
                part="snippet,statistics"
            ).execute()
        else:
            video_information_json = self.youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                order="viewCount",
                publishedAfter=start_time,
                publishedBefore=end_time,
                maxResults=500
            ).execute()

        print(type(video_information_json))  # prints the type of video_information_json
        print(video_information_json)  # prints the content of video_information_json
        return video_information_json
        #
        # if isinstance(video_information_json, dict):
        #     print(video_information_json)
        #     return self.json_to_df_information(video_information_json)
        # else:
        #     raise TypeError(f"Unexpected type {type(video_information_json)} for video_information_json")

    def json_to_df_information(self, video_information_json):
        # Check if 'items' key exists in the response
        if 'items' not in video_information_json:
            raise Exception("Invalid response: 'items' key not found in the response.")

        # Check if there's more than one item in the response
        if len(video_information_json['items']) > 1:
            extracted_fields_video_information = [
                {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'publishdate': item['snippet']['publishedAt']
                }
                for item in video_information_json['items']
            ]
            df_video_information = pd.DataFrame(extracted_fields_video_information)
            return df_video_information

        else:  # We're dealing with a single video
            item = video_information_json['items'][0]
            extracted_fields_video_information = [
                {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'publishdate': item['snippet']['publishedAt']
                }
                for item in video_information_json['items']
            ]

            df_video_information = pd.DataFrame(extracted_fields_video_information)
            return df_video_information

    def video_statistics(self, video_id):
        if video_id is not None:
            video_statistics_json = self.youtube.videos().list(
                id=video_id,
                part="statistics",
                maxResults=500
            ).execute()
        else:
            video_statistics_json = self.youtube.videos().list(
                part="statistics",
                maxResults=500
            ).execute()

        print(video_statistics_json)
        return video_statistics_json

    def json_to_df_statistics(self):
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

        df_video_statistics = pd.DataFrame(extracted_fields_video_statistics)
        return df_video_statistics


class YouTubeDataProcessor:
    def __init__(self):
        self.df_video_information = None
        self.df_video_statistics = None

    def process_data(self, df_video_information, df_video_statistics):
        self.df_video_information = df_video_information
        self.df_video_statistics = df_video_statistics
        self.df_video_combined = self.df_video_information.merge(self.df_video_statistics, how='left', on='id')
        print(self.df_video_combined)
        print(self.df_video_combined.columns)

    def get_combined_dataframe(self):
        return self.df_video_combined


class YouTubeDataAnalyzer:
    def __init__(self):
        self.df_video_combined = None

    def calculate_kpis(self):
        self.df_video_combined['likes'] = pd.to_numeric(self.df_video_combined['likes'])
        self.df_video_combined['comments'] = pd.to_numeric(self.df_video_combined['comments'])
        self.df_video_combined['viewcount'] = pd.to_numeric(self.df_video_combined['viewcount'])
        print(self.df_video_combined.dtypes)

        self.df_video_combined['publishdate'] = pd.to_datetime(self.df_video_combined['publishdate']).dt.date
        self.df_video_combined['days_since_published'] = (
                    pd.Timestamp.today().date() - self.df_video_combined['publishdate']).dt.days

        self.df_video_combined['views_per_day'] = self.df_video_combined['viewcount'] / self.df_video_combined[
            'days_since_published']
        self.df_video_combined['engagement_rate'] = (self.df_video_combined['likes'] + self.df_video_combined[
            'comments']) / self.df_video_combined['viewcount']
        self.df_video_combined['engagement_per_day'] = (self.df_video_combined['likes'] + self.df_video_combined[
            'comments']) / self.df_video_combined['days_since_published']
        # self.df_video_combined['performance_kpi'] = weights['views'] * self.df_video_combined['viewcount'] + weights['likes'] * self.df_video_combined['likes'] + weights['favourites'] * self.df_video_combined['favourites'] + weights['comments'] * self.df_video_combined['comments']
        self.df_video_combined['viral_score'] = self.df_video_combined['viewcount'] * self.df_video_combined[
            'engagement_rate']
        self.df_video_combined['views_per_day_weighted_mavg'] = self.df_video_combined['views_per_day'].ewm(
            span=7).mean()
        # self.df_video_combined['days_since_published_decay'] = decay_rate ** self.df_video_combined['days_since_published']
        # self.df_video_combined['views_decay_adjusted'] = self.df_video_combined['viewcount'] / self.df_video_combined['days_since_published_decay']

        return self.df_video_combined


class DataVisualizer:
    @staticmethod
    def plot_kpi(df, column, title):
        df_sorted = df.sort_values(column, ascending=False)

        fig = px.bar(
            df_sorted[:20],
            x='title',
            y=column,
            title=title,
            labels={column: title, 'title': 'Video Title'},
            width=800,
            height=400
        )

        fig.update_layout(xaxis_tickangle=-45)
        fig.show()


if __name__ == "__main__":
    api_key = cfg.api_key  # replace with your own API key

    # Create instances of the classes
    api = YouTubeAPI(api_key)
    processor = YouTubeDataProcessor()
    analyzer = YouTubeDataAnalyzer()
    visualiser = DataVisualizer()

    # Define the necessary arguments
    query = None  # Set to None if you want to fetch video information by video_id only
    start_time = None  # Set to the desired start time in the format "YYYY-MM-DDTHH:MM:SSZ"
    end_time = None  # Set to the desired end time in the format "YYYY-MM-DDTHH:MM:SSZ"
    video_id = "Byb0DLtNN_0"  # Set to the desired video ID

    # Call the methods of each class
    video_information_json = api.video_information(query, start_time, end_time, video_id)
    df_video_information = api.json_to_df_information(video_information_json)
    video_statistics_json = api.video_statistics(video_id)
    df_video_statistics = api.json_to_df_statistics()

    # Process the data
    processor.process_data(df_video_information, df_video_statistics)
    # Get the processed data from the processor
    df_video_combined = processor.get_combined_dataframe()
    print(df_video_combined)

    # Pass the processed data to the analyzer
    analyzer.df_video_combined = df_video_combined
    print(analyzer.df_video_combined)

    # Get the processed data from the analyser
    df_video_combined = analyzer.calculate_kpis()
    print(df_video_combined)

    # Pass the processed data to the visualser
    visualiser.plot_kpi = df_video_combined
    print(visualiser.df_video_combined)

    #
    df_video_combined = visualiser.calculate_kpis()
    print(df_video_combined.columns)



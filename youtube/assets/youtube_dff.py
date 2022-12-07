import pandas as pd
from googleapiclient.discovery import build
from dateutil import parser
import isodate
import re
import emoji
import pymongo


#
class youtube_creator_dataframe:

    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.api_key = "AIzaSyAYhHLmgXIRP8gsX5mGZywEcwJGu0kBr0k"
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_playlist_id(self, youtube):
        """ fetch the playlist id """
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=self.channel_id)
        response = request.execute()
        plalist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return plalist_id

    def get_video_ids(self, youtube, playlist_id):
        """ getting video_id of youtubber """
        video_ids = []

        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        while next_page_token is not None:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token)
            response = request.execute()

            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')

        return video_ids

    def get_video_details(self, youtube, video_ids):
        all_video_info = []

        for i in range(0, len(video_ids), 50):
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=','.join(video_ids[i:i + 50])
            )
            response = request.execute()

            for video in response['items']:
                stats_to_keep = {
                    'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt', 'categoryId'],
                    'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                    'contentDetails': ['duration', 'definition', 'caption']
                }
                video_info = {}
                video_info['video_id'] = video['id']

                for k in stats_to_keep.keys():
                    for v in stats_to_keep[k]:
                        try:
                            video_info[v] = video[k][v]
                        except:
                            video_info[v] = None

                all_video_info.append(video_info)

        return pd.DataFrame(all_video_info)

    def get_comments_in_videos(self, youtube, video_ids):
        """
        """
        all_comments = {}

        for video_id in video_ids:
            try:
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id
                )
                response = request.execute()

                comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in
                                     response['items'][0:10]]

                #             comments_in_video_info = {'video_id': video_id, 'comments': comments_in_video}

                all_comments[video_id] = comments_in_video

            except:
                continue
                # When error occurs - most likely because comments are disabled on a video

        return all_comments

    def raw_data_to_dataframe(self):
        video_df = pd.DataFrame()

        get_playlist_id_youtuber = self.get_playlist_id(self.youtube)

        get_video_id_list = self.get_video_ids(self.youtube, get_playlist_id_youtuber)
        video_info_youtuber = self.get_video_details(self.youtube, get_video_id_list)

        comment_dict = self.get_comments_in_videos(self.youtube, get_video_id_list)

        video_info_youtuber['commenttext'] = video_info_youtuber['video_id'].map(comment_dict)

        # append video data together and comment data toghether
        video_df = pd.concat([video_info_youtuber, video_df])

        return video_df

    def no_of_words(self, title):
        # removes all speciall character from the word
        title = re.sub(r"[^a-zA-Z0-9]+", ' ', title)
        count = 0
        for letter in title:
            if letter == ' ':
                count += 1
        return count + 1

    def day_predictor(self, pushblishDayName):
        day = pushblishDayName
        if day in ['Sunday', 'Saturday']:
            return 'weekend'
        else:
            return 'weekday'

    def emoji_counter(self, comments):
        total_count_emoji = 0
        try:
            for emojis in comments:
                emoji_count = emoji.emoji_count(emojis, unique=True)
                total_count_emoji = total_count_emoji + emoji_count
        except Exception:
            print(Exception)
        return total_count_emoji

    def minutes_category(self, secs):
        min = round(secs / 60)
        if min <= 3:
            return "0-3mins"
        elif 3 < min <= 6:
            return "3-6mins"
        elif 6 < min <= 10:
            return "6-10mins"
        elif 10 < min <= 15:
            return "10-15mins"
        elif 15 < min <= 20:
            return "15-20mins"
        elif 20 < min <= 25:
            return "20-25mins"
        elif 25 < min <= 30:
            return "25-30mins"
        elif 30 < min <= 40:
            return "30-40mins"
        elif 40 < min <= 60:
            return "40-60mins"
        elif 60 < min <= 90:
            return "1-1.5h"
        elif 90 < min <= 120:
            return "1.5-2h"
        else:
            return "greater-2h"

    def raw_data_clean_data(self):

        dataframe = self.raw_data_to_dataframe()
        dff = dataframe
        dff['viewCount'] = dataframe['viewCount'].apply(lambda x: 0 if x is None else int(x))
        dff['likeCount'] = dataframe['likeCount'].apply(lambda x: 0 if x is None else int(x))
        dff['commentCount'] = dataframe['commentCount'].apply(lambda x: 0 if x is None else int(x))
        # Create publish day (in the week) column
        dff['publishedAt'] = dataframe['publishedAt'].apply(lambda x: parser.parse(x))
        dff['pushblishDayName'] = dataframe['publishedAt'].apply(lambda x: x.strftime("%A"))
        # convert duration to seconds
        dff['durationSecs'] = dataframe['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())
        dff['tagsCount'] = dataframe['tags'].apply(lambda x: 0 if x is None else len(x))
        dff['titleLength'] = dataframe['title'].apply(lambda x: len(x))

        dff['no_words_title'] = dataframe['title'].apply(self.no_of_words)
        dff['weekdayVsweekend'] = dataframe['pushblishDayName'].apply(self.day_predictor)
        dff['emoji_counts'] = dataframe['commenttext'].apply(self.emoji_counter)
        dff['durationmins'] = dataframe['durationSecs'].apply(self.minutes_category)

        return dff

    def save_data_mangodb(self):
        client = pymongo.MongoClient(
            "mongodb+srv://Amrpur:Amrith123@amr.byx5b8y.mongodb.net/?retryWrites=true&w=majority")
        db = client[self.channel_id]
        clean_dff = self.raw_data_clean_data()
        db_channel_name = clean_dff.loc[0, "channelTitle"]
        collection = db[db_channel_name]

        clean_dff.reset_index(inplace=True)
        clean_data_dict = clean_dff.to_dict("records")
        # Insert collection
        collection.insert_many(clean_data_dict)
        return 1

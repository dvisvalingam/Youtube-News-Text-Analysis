# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 20:28:04 2019

@author: aneesh sandhir (as6bw) & devan Visvalingam (dv5mx)
"""
from apiclient.discovery import build
import sys
import glob

class Playlist_Comment_Scraper():
    
    def __init__(self, search_string_input, search_type_input, combine_comments_file_name):
        self.search_string = search_string_input
        self.search_type = search_type_input
        self.combine_comments_file_name = combine_comments_file_name
        # API Key is set using the Google Developer Console and is constant for our purposes  
        self.api_key = "AIzaSyDiUlx08HiRDjrXVIbwjPX9pooNNsVZ64o"
        # Creates a build object of type youtube as an attribute allowing for it to be refrenced in any of the classes functions 
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def create_file_name(self, name_of_video):
        # Apends the file extension for a text file before scrubing a given string of any characters which would prevent it from creating with that name on certain Windows Operating Systems
        restricted_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*' ]
        output_file_name = name_of_video + '.txt'
        for character in restricted_characters:
            output_file_name = output_file_name.replace(character,'-')
        return output_file_name
    
    def get_top_playlist_response(self):
        if self.search_type == 'playlist':
            # Leverages the search feature of the Youtube Data API to identify a playlist and retreive its 20 most recent videos
            search_response = self.youtube.search().list(q = self.search_string, part = 'snippet', type = 'playlist', maxResults = 1).execute()
            playlist_id = search_response['items'][0]['id']['playlistId']
            playlist_response = self.youtube.playlistItems().list(playlistId = playlist_id, part = 'snippet', maxResults = 20).execute()
        elif self.search_type == 'channel':
            # Leverages the search feature of the Youtube Data API to identify a channel and retreive its 20 most recent videos from it's Uploads playlist
            search_response = self.youtube.search().list(q = self.search_string, part = 'snippet', type = 'channel', maxResults = 1).execute()
            channel_id = search_response['items'][0]['id']['channelId']
            channel_response = self.youtube.channels().list(id = channel_id, part = 'contentDetails').execute()    
            playlist_id = channel_response ['items'][0]['contentDetails']['relatedPlaylists']['uploads']    
            playlist_response= self.youtube.playlistItems().list(playlistId = playlist_id, part = 'snippet', maxResults = 20).execute()
        return playlist_response
        
    def export_all_comments_on_a_playlist(self):
        console = sys.stdout
        # Initialize a counter which tracks the number of singly posted comments on a playlist
        total_unique_comments = 0
        # Creates a file with the name of the video to which it writes all of the comments to
        for video in self.get_top_playlist_response()['items']:
            sys.stdout = open(self.create_file_name(video['snippet']['title']), 'a')
            # Retreives the first 100 comments on a given video
            comment_thread = self.youtube.commentThreads().list(videoId = video['snippet']['resourceId']['videoId'], part = 'snippet', maxResults = 100).execute()
            # Attempts to retreives the token allowing for the retreival of the next 100 comments on a given video
            try:
                next_page_token = comment_thread['nextPageToken']
            except:
                # Allows the next_page_token to not take on any value enables the function to collect all the comments on a video with less than 100 comments
                next_page_token = None
            # Catches any comment posted consecutively and prevents it from being overrepresented in the output file
            potential_duplicate  = ''
            if next_page_token != None:
                while next_page_token != None:
                    for comment in comment_thread['items']:
                        # Cleanses a given comment of emojis and ethnic writing systems
                        comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay'].encode('ascii', 'ignore').decode('ascii')
                        if comment_text != potential_duplicate:
                            # Print the text of a comment so long as it is not a dupliate and increments the comment counter
                            print(comment_text)
                            total_unique_comments += 1
                        potential_duplicate = comment_text
                    # Retreives the first 100 comments on a given video
                    comment_thread = self.youtube.commentThreads().list(videoId = video['snippet']['resourceId']['videoId'], part = 'snippet', maxResults = 100, pageToken = next_page_token).execute()
                    # Attempts to retreives the token allowing for the retreival of the next 100 comments on a given video
                    try:
                        next_page_token = comment_thread['nextPageToken']
                    except:
                        break
            for comment in comment_thread['items']:
                # Cleanses a given comment of emojis and ethnic writing systems
                comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay'].encode('ascii', 'ignore').decode('ascii')
                if comment_text != potential_duplicate:
                    # Print the text of a comment so long as it is not a dupliate and increments the comment counter
                    print(comment_text)
                    total_unique_comments += 1
                potential_duplicate = comment_text
            # Ceases to write comments to the file created at the begining of the loop
            sys.stdout = console
        # Creates a single text file which contains all the comments for a given playlist   
        read_files = glob.glob("*.txt")
        with open(self.create_file_name(self.combine_comments_file_name), "wb") as outfile:
            for f in read_files:
                with open(f, "rb") as infile:
                    outfile.write(infile.read())
        return total_unique_comments
    
#==================================================
tSeries = Playlist_Comment_Scraper('T-Series', 'channel','Tu Cheez Badi Hai')
tSeries.export_all_comments_on_a_playlist()
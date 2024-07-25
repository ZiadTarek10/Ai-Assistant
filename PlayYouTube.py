from googleapiclient.discovery import build

def get_youtube_video(song):
    try:
        query = song.replace("play ", "")  # Fix typo: replace "paly" with "play"
        api_key = 'AIzaSyBLPbg6lwfvZxQjqck5ka8bU4LDShxXOkY'  # Replace with your actual YouTube API key
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=query
        )
        response = request.execute()
        
        video_id = response['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        return str(e)

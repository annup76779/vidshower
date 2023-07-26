import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials

# Set up the Google Drive API credentials
# Make sure you have the necessary credentials file (client_secrets.json) and token file (token.json)
# Replace 'YOUR_CREDENTIALS_FILE.json' with the path to your credentials file
credentials_file = 'client_secret.json'
scopes = ['https://www.googleapis.com/auth/drive.readonly']
with open(os.path.join(os.path.dirname(os.path.basename(__file__)), credentials_file), "r") as config:
    config = json.load(config)
    credentials = Credentials.from_authorized_user_info(info=config.get("installed"), scopes=scopes)


# Build the service
service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
# https://drive.google.com/drive/folders/11hpxA7qzIOYetBiIsOpAC4DXU_xvLmhG?usp=sharing
# Set the folder ID of the Google Drive folder containing the videos
folder_id = '11hpxA7qzIOYetBiIsOpAC4DXU_xvLmhG'


def list_files_in_folder(folder_id):
    files = []
    page_token = None
    while True:
        # Fetch a batch of files (maximum 100 per request)
        files_obj = service.files()
        response = files_obj.list(q=f"'{folder_id}' in parents",
                                        fields="files(name, id)",
                                        pageSize=500,
                                        pageToken=page_token).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return files


def download_videos_from_folder(folder_id):
    # Retrieve the list of files in the folder
    files = list_files_in_folder(folder_id)
    print(len(files))

    # Iterate over the files and download them
    for i, file in enumerate(files):
        file_name = "video%d.mp4" % (i+1)
        file_id = file['id']
        request = service.files().get_media(fileId=file_id)

        # Create a new directory to save the downloaded videos (if it doesn't exist)
        save_directory = os.path.join(os.path.dirname(__file__), '../static', "videos")
        os.makedirs(save_directory, exist_ok=True)

        # Download the video file
        with open(os.path.join(save_directory, file_name), 'wb') as video_file:
            downloader = MediaIoBaseDownload(video_file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloading {file_name} - {int(status.progress() * 100)}%")

    print("Video download complete.")

# Call the function to download videos from the specified folder
download_videos_from_folder(folder_id)

import streamlit as st
import yt_dlp as youtube_dl
import ffmpeg
from datetime import datetime
import os

"""
TODO:
Add Exception handling
Use Pathlib
Default pathname 
In directory
Deploy to Github
Add Readme
Add tab for screenshot extractor
Docker build
Add Extension support(GIF and other formats) -- least priority
"""


# Function to download and trim video
def download_and_trim(url, start_time, end_time, output_filename):
    with youtube_dl.YoutubeDL({"format": "best"}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = info_dict["url"]
        stream = ffmpeg.input(video_url, ss=start_time, to=end_time)
        stream = ffmpeg.output(stream, output_filename)
        ffmpeg.run(stream)


# Create a unique filename
def create_unique_filename(base_name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name, ext = os.path.splitext(base_name)
    return f"{name}_{timestamp}{ext}"


# Streamlit interface
st.title("YouTube Video Trimmer")
st.markdown(
    """
    Welcome to the YouTube Video Trimmer! 
    This tool allows you to download and trim parts of YouTube videos. 
    Just enter the URL of the YouTube video, specify the start and end times for the clip, 
    and hit the button to process. You can then download the trimmed video.
    """
)

# Input fields
yt_url = st.text_input("Enter YouTube URL")
start = st.text_input("Enter Start Time (HH:MM:SS)")
end = st.text_input("Enter End Time (HH:MM:SS)")
default_output_name = "output.mp4"
output = st.text_input("Enter Output Filename", value=default_output_name)

if st.button("Download and Trim Video"):
    if output == default_output_name:
        output = create_unique_filename(output)
    download_and_trim(yt_url, start, end, output)
    st.video(output)
    with open(output, "rb") as file:
        st.download_button(
            label="Download Video",
            data=file,
            file_name=output,
            mime="video/mp4",
        )
    # os.remove(output)  # Optional: remove the file after downloading

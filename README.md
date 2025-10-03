# 🎬 YT-Trimmer

## Description

This Streamlit web application allows users to download specific time segments from YouTube videos as MP4 files. Simply provide a YouTube URL, define the desired start and end times for the segment, and the application will process and provide the video for download.

-----


## Dependencies

To run this application, you will need to install the following Python libraries:

  * `streamlit`
  * `yt-dlp` (for `video_utils.py` - handles video fetching and downloading)
  * `ffmpeg` (must be installed on your system and accessible in your PATH for `yt-dlp` to cut video segments)

-----

## Installation and Running Locally

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/YT-Trimmer.git
    cd YT-Trimmer
    ```

2.  **Install Dependencies:**

    ```bash
    pip install streamlit yt-dlp
    ```

3.  **Install FFmpeg:**
    FFmpeg is an external tool required by `yt-dlp` for cutting video segments. You can download it from the official FFmpeg website: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html). Ensure it is added to your system's PATH.

4.  **Run the App:**
    Navigate to the directory containing `app.py` in your terminal and run:

    ```bash
    streamlit run main.py
    ```

    Your web browser should automatically open the application.
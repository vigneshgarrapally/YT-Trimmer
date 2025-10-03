# app.py

import os
import streamlit as st
import video_utils
import datetime
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="YouTube Segment Downloader",
    page_icon="🎬",
    layout="centered",
)

# --- App State Initialization ---
if "video_info" not in st.session_state:
    st.session_state.video_info = None
if "downloaded_path" not in st.session_state:
    st.session_state.downloaded_path = None
if "error_message" not in st.session_state:
    st.session_state.error_message = None
# Add state for the input method, defaulting to Manual
if "input_method" not in st.session_state:
    st.session_state.input_method = "Manual Entry"


# --- Helper Functions ---
def seconds_to_hms_str(seconds: int) -> str:
    """Converts seconds to a HH:MM:SS string for display."""
    seconds = int(seconds)  # Ensure it's an integer for timedelta
    return str(datetime.timedelta(seconds=seconds))


def hms_str_to_seconds(hms_str: str) -> int | None:
    """Converts various HH:MM:SS string formats to total seconds."""
    match = re.match(r"(?:(\d+):)?(\d{1,2}):(\d{1,2})$", hms_str.strip())
    if not match:
        return None  # Invalid format

    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes)
    seconds = int(seconds)

    if not (0 <= minutes < 60 and 0 <= seconds < 60):
        return None  # Invalid minutes or seconds

    return hours * 3600 + minutes * 60 + seconds


# --- UI Layout ---
st.title("🎬 YouTube Segment Downloader")
st.markdown(
    "Enter a YouTube URL, select a time segment, and download it as an MP4 file."
)

# Create a directory for downloads if it doesn't exist
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)


# --- Step 1: URL Input and Info Fetching ---
url = st.text_input(
    "Enter the YouTube Video URL:",
    placeholder="https://www.youtube.com/watch?v=...",
    key="youtube_url",
)

if st.button("Get Video Info", key="fetch_info"):
    # Reset state on new URL fetch
    st.session_state.video_info = None
    st.session_state.downloaded_path = None
    st.session_state.error_message = None

    if url:
        with st.spinner("🔍 Fetching video details..."):
            info, error = video_utils.get_video_info(url)
            if error:
                st.session_state.error_message = error
            else:
                st.session_state.video_info = info
    else:
        st.session_state.error_message = "Please enter a YouTube URL."

if st.session_state.error_message and not st.session_state.video_info:
    st.error(st.session_state.error_message)


# --- Step 2: Segment Selection and Download ---
if st.session_state.video_info:
    info = st.session_state.video_info
    duration = int(info["duration"])
    title = info["title"]

    st.subheader("Video Details")
    st.write(f"**Title:** {title}")
    st.write(f"**Total Duration:** {seconds_to_hms_str(duration)}")

    st.subheader("Select Time Segment")

    segment_start_sec, segment_end_sec = 0, 0
    is_segment_valid = False

    st.markdown(
        "Enter start and end times in **HH:MM:SS** or **MM:SS** format."
    )
    col1, col2 = st.columns(2)
    with col1:
        manual_start_str = st.text_input("Start Time:", "00:00:00")
    with col2:
        manual_end_str = st.text_input(
            "End Time:", seconds_to_hms_str(min(duration, 60))
        )

    # Validate Manual Input
    start_s = hms_str_to_seconds(manual_start_str)
    end_s = hms_str_to_seconds(manual_end_str)

    if start_s is None or end_s is None:
        st.error(
            "Invalid time format. Please use HH:MM:SS, H:MM:SS, or MM:SS."
        )
    elif not (0 <= start_s < duration and 0 < end_s <= duration):
        st.error(
            f"Times must be within the video duration (00:00:00 to {seconds_to_hms_str(duration)})."
        )
    elif start_s >= end_s:
        st.error("Start time must be before end time.")
    else:
        is_segment_valid = True
        segment_start_sec, segment_end_sec = start_s, end_s
        st.success(
            f"Selected range: **{seconds_to_hms_str(start_s)}** to **{seconds_to_hms_str(end_s)}**"
        )

    # --- Download Section ---
    if is_segment_valid:
        default_filename = video_utils.create_safe_filename(title)
        output_filename = st.text_input(
            "Output filename:",
            value=default_filename,
            key="output_filename_input",
        )

        if st.button("Download Segment", key="download_segment"):
            if not output_filename:
                st.error("Output filename cannot be empty.")
            else:
                output_path = os.path.join(DOWNLOADS_DIR, output_filename)
                with st.spinner(
                    "Downloading segment... this may take a moment."
                ):
                    success, result_msg = video_utils.download_video_segment(
                        url, segment_start_sec, segment_end_sec, output_path
                    )
                    if success:
                        st.session_state.downloaded_path = result_msg
                        st.session_state.error_message = None
                    else:
                        st.session_state.error_message = result_msg
                        st.session_state.downloaded_path = None


# --- Step 3: Display Result and Provide Download Link ---
if st.session_state.error_message and not st.session_state.downloaded_path:
    st.error(st.session_state.error_message)

if st.session_state.downloaded_path:
    filepath = st.session_state.downloaded_path
    filename = os.path.basename(filepath)

    st.success("✅ Segment successfully downloaded!")
    try:
        st.video(filepath)
        with open(filepath, "rb") as file:
            st.download_button(
                label="📥 Download Video File",
                data=file,
                file_name=filename,
                mime="video/mp4",
            )
    except FileNotFoundError:
        st.error("The downloaded file could not be found. Please try again.")
        st.session_state.downloaded_path = None

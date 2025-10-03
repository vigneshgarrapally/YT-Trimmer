# video_utils.py

import logging
import os
import re
import shlex
import subprocess
from typing import Dict, Optional, Tuple

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

# --- Setup Logging ---
# Configures a logger for this module.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_video_info(url: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Extracts video information (duration, title) using yt-dlp.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        Tuple[Optional[Dict], Optional[str]]: A tuple containing a dictionary with
        'duration' and 'title' on success, and an error message string on failure.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "force_generic_extractor": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            duration = info_dict.get("duration")
            title = info_dict.get("title")

            if not duration or not title:
                logger.error(
                    f"Could not extract necessary info for URL: {url}"
                )
                return None, "Failed to extract video duration or title."

            logger.info(f"Fetched info for '{title}': {duration} seconds.")
            return {"duration": duration, "title": title}, None

    except (DownloadError, ExtractorError) as e:
        logger.error(f"yt-dlp error for URL {url}: {e}")
        return (
            None,
            f"Invalid YouTube URL or video not accessible. Please check the link. (Error: {e})",
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_video_info: {e}")
        return None, "An unexpected error occurred while fetching video info."


def create_safe_filename(title: str) -> str:
    """
    Generates a filesystem-safe filename from a video title.

    Args:
        title (str): The video title.

    Returns:
        str: A sanitized filename ending with .mp4.
    """
    # Remove invalid characters for most filesystems
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    # Replace spaces with underscores and limit length
    safe_title = "_".join(safe_title.split()).strip()[:100]
    return f"{safe_title}.mp4"


def download_video_segment(
    url: str, start_time: int, end_time: int, output_path: str
) -> Tuple[bool, str]:
    """
    Downloads a specific time segment of a YouTube video using the yt-dlp command.

    Args:
        url (str): The full URL of the YouTube video.
        start_time (int): The starting timestamp in seconds.
        end_time (int): The ending timestamp in seconds.
        output_path (str): The path to save the output file.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean for success/failure
        and a message (output path on success, error details on failure).
    """
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Convert seconds to HH:MM:SS format for yt-dlp
    start_hhmmss = (
        f"{start_time//3600}:{(start_time%3600)//60}:{start_time%60}"
    )
    end_hhmmss = f"{end_time//3600}:{(end_time%3600)//60}:{end_time%60}"

    download_section = f"*{start_hhmmss}-{end_hhmmss}"

    command = [
        "yt-dlp",
        "--extractor-args",
        "youtube:player-client=default,-tv_simply",
        "--download-sections",
        download_section,
        "--force-keyframes-at-cuts",  # For more accurate cuts
        "-o",
        output_path,
        "--recode-video",
        "mp4",
        url,
    ]

    logger.info(
        f"Executing command: {' '.join(shlex.quote(c) for c in command)}"
    )

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        logger.info(f"yt-dlp STDOUT: {result.stdout}")
        logger.info(f"Successfully downloaded segment to: {output_path}")
        return True, os.path.abspath(output_path)

    except FileNotFoundError:
        error_msg = "'yt-dlp' command not found. Please ensure it is installed and in your system's PATH."
        logger.error(error_msg)
        return False, error_msg
    except subprocess.CalledProcessError as e:
        error_msg = f"yt-dlp error (Code {e.returncode}):\n{e.stderr}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred during download: {e}"
        logger.error(error_msg)
        return False, error_msg

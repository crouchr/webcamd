import os


def get_version():
    if 'VERSION' in os.environ:
        version = os.environ['VERSION']
    else:
        version = 'IDE-1.0.0'   # i.e. running in PyCharm

    return version


def get_video_length():
    """
    Set webcam video duration in Docker Compose ENV
    """
    if 'VIDEO_SECS' in os.environ:
        video_length_secs = int(os.environ['VIDEO_SECS'])
    else:
        video_length_secs = 5
        return video_length_secs


def get_video_preamble():
    """
    Set webcam video preamble duration in Docker Compose ENV
    """

    if 'PREAMBLE_SECS' in os.environ:
        preamble_secs = int(os.environ['PREAMBLE_SECS'])
    else:
        preamble_secs = 5

    return preamble_secs


def get_min_solar():
    """
    Set minimum value of solar level to take video in (watts/metre-squared)
    """

    if 'MIN_SOLAR' in os.environ:
        min_solar = os.environ['MIN_SOLAR']     # a float
    else:
        min_solar = 1.0

    return min_solar


def get_mins_between_videos():
    """
    Set time between consecutive videos
    """

    if 'MINS_BETWEEN_VIDEOS' in os.environ:
        mins_between_videos = int(os.environ['MINS_BETWEEN_VIDEOS'])
    else:
        mins_between_videos = 15

    return mins_between_videos
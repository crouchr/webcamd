import os


def get_version():
    if 'VERSION' in os.environ:
        version = os.environ['VERSION']
    else:
        version = 'IDE-1.0.0'   # i.e. running in PyCharm

    return version


def get_stage():
    if 'STAGE' in os.environ:
        stage = os.environ['STAGE']
    else:
        stage = 'DEV'   # i.e. running in PyCharm

    return stage


def get_webcam_service_endpoint():
    if 'STAGE' in os.environ and os.environ['STAGE'] == 'PRD':
        webcam_service_endpoint_base = 'http://webcam-service:9504'
    else:
        webcam_service_endpoint_base = 'http://192.168.1.180:9504'

    return webcam_service_endpoint_base


def get_twitter_service_endpoint():
    if 'STAGE' in os.environ and os.environ['STAGE'] == 'PRD':
        twitter_service_endpoint_base = 'http://webcam-service:9506'
    else:
        twitter_service_endpoint_base = 'http://192.168.1.180:9506'

    return twitter_service_endpoint_base


def get_cumulusmx_endpoint():
    if 'STAGE' in os.environ and os.environ['STAGE'] == 'PRD':
        cumulusmx_endpoint = 'http://cumulusmx:8998/api/data/currentdata'
    else:
        cumulusmx_endpoint = 'http://192.168.1.180:8998/api/data/currentdata'

    return cumulusmx_endpoint


def get_video_length():
    """
    Set webcam video duration in Docker Compose ENV
    """
    if 'VIDEO_SECS' in os.environ:
        video_length_secs = int(os.environ['VIDEO_SECS'])
    else:
        video_length_secs = 20
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
        min_solar = 0.5

    return min_solar


def get_max_solar():
    """
    Set maximum value of solar level to take video in (watts/metre-squared)
    i.e. get reflections from window when curtains are closed
    """

    if 'MAX_SOLAR' in os.environ:
        max_solar = os.environ['MAX_SOLAR']     # a float
    else:
        max_solar = 130.0

    return max_solar


def get_mins_between_videos():
    """
    Set time between consecutive videos
    """

    if 'MINS_BETWEEN_VIDEOS' in os.environ:
        mins_between_videos = int(os.environ['MINS_BETWEEN_VIDEOS'])
    else:
        mins_between_videos = 60    # was 15

    return mins_between_videos


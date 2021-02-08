# Infinite loop for grabbing sky videos and posting to Twitter if there is sufficient light
# TODO : only tweet if other weather conditions are interesting e.g. wind ? minimum
# This is basically a script showing how to use the various microservices

import time
import uuid
import traceback
from pprint import pprint

import call_rest_api
import definitions
import get_cumulus_weather_info
import get_env


def get_light_level(uuid):
    """
    Read lux/watts levels from light sensor
    """
    query = {}                                  # API call to light-service
    query['app_name'] = 'webcamd'
    query['uuid'] = uuid

    light_service_listen_port = 9503
    light_service_endpoint_base = 'http://192.168.1.180:' + light_service_listen_port.__str__()

    status_code, response_dict = call_rest_api.call_rest_api(light_service_endpoint_base + '/get_lux', query)

    lux = response_dict['lux']
    sky_condition = response_dict['sky_condition']
    watts = round(response_dict['watts'], 2)

    return int(lux), watts, sky_condition


def send_tweet(tweet_text, filename, uuid):
    """
    Send a Tweet with a video file
    """
    query = {}                                  # API call to twitter-service
    query['app_name'] = 'take_sky_webcamd'
    query['uuid'] = uuid
    query['tweet_text'] = tweet_text
    query['hashtag_arg'] = 'metminiwx'          # do not supply the #
    query['lat'] = 51.4151                      # Stockcross
    query['lon'] = -1.3776                      # Stockcross
    query['video_pathname'] = filename

    twitter_service_endpoint_base = 'http://192.168.1.180:9506'
    status_code, response_dict = call_rest_api.call_rest_api(twitter_service_endpoint_base + '/send_video', query)
    # print('status_code=' + status_code.__str__())
    # pprint(response_dict)

    if response_dict['tweet_sent'] == True:
        print('Tweet sent OK, uuid=' + uuid.__str__())
    else:
        print('Error : failed to send Tweet, uuid=' + uuid.__str__())


def main():
    try:
        crf = 19                                # H264 encoding quality parameter
        my_app_name = 'webcamd'

        video_length_secs = get_env.get_video_length()
        preamble_secs = get_env.get_video_preamble()
        min_solar = get_env.get_min_solar()
        mins_between_videos = get_env.get_mins_between_videos()

        webcam_query = {}                       # API call to webcam-service
        webcam_query['app_name'] = my_app_name
        webcam_query['video_length_secs'] = video_length_secs
        webcam_query['preamble_secs'] = preamble_secs

        print(my_app_name + ' started...')

        while True:
            this_uuid = uuid.uuid4().__str__()          # unique uuid per cycle

            cumulus_weather_info = get_cumulus_weather_info.get_key_weather_variables()     # REST API call

            _, solar, sky_condition = get_light_level(this_uuid)
            if solar <= min_solar:                  # do not bother taking video if it is too dark
                print(time.ctime() + ' : light level is below ' + min_solar.__str__() + ' W, so sleeping... solar=' + solar.__str__())
                time.sleep(600)                     # 10 minutes
                continue

            webcam_query['uuid'] = this_uuid
            print('Grabbing webcam mp4 video and a jpg..., uuid=' + this_uuid)
            status_code, response_dict = call_rest_api.call_rest_api(definitions.webcam_service_endpoint_base + '/get_video', webcam_query)
            mp4_filename = response_dict['video_filename']
            jpeg_filename = response_dict['jpeg_filename']

            print('wrote webcam video to : ' + mp4_filename + ', uuid=' + this_uuid)
            print('wrote webcam jpeg to  : ' + jpeg_filename + ', uuid=' + this_uuid)

            filename = mp4_filename.split('/')[-1]      # ignore the filepath

            # Tweet the video
            tweet_text = cumulus_weather_info['Beaufort'] + ' (max=' + cumulus_weather_info['HighBeaufortToday'] + ')' + \
                ', cbase=' + cumulus_weather_info['Cloudbase'].__str__() + ' ' + cumulus_weather_info['CloudbaseUnit'] + \
                ', ' + cumulus_weather_info['Pressure'].__str__() + ' ' + cumulus_weather_info['PressUnit'] + \
                ', trend=' + cumulus_weather_info['PressTrend'].__str__() + \
                ', temp=' + cumulus_weather_info['OutdoorTemp'].__str__() + cumulus_weather_info['TempUnit'] + \
                ', wind_chill=' + cumulus_weather_info['WindChill'].__str__() + cumulus_weather_info['TempUnit'] + \
                ', dew_point=' + cumulus_weather_info['OutdoorDewpoint'].__str__() + cumulus_weather_info['TempUnit'] + \
                ', ' + cumulus_weather_info['DominantWindDirection'] + \
                ', last_rain=' + cumulus_weather_info['LastRainTipISO'] + \
                ', fcast=* ' + cumulus_weather_info['Forecast'] + ' *'\
                ', solar=' + solar.__str__() + \
                ' ' + filename

            # Tweet is too long
            # ', sunrise=' + cumulus_weather_info['Sunrise'] + \
            # ', sunset=' + cumulus_weather_info['Sunset'] + \

            print(tweet_text)
            send_tweet(tweet_text, mp4_filename, this_uuid)

            sleep_secs = mins_between_videos * 60
            print('----------------------------------------------')
            print(time.ctime() + ' sleeping for ' + sleep_secs.__str__() + ' ...')
            time.sleep(sleep_secs)

    except Exception as e:
        traceback.print_exc()


if __name__ == '__main__':
    main()

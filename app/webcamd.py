# Infinite loop for grabbing sky videos and posting to Twitter if there is sufficient light
# TODO : only tweet if other weather conditions are interesting e.g. wind ? minimum
# This is basically a script showing how to use the various microservices
# todo : no need to tweet hourly in the night so make it smarter

import time
import uuid
import traceback
from pprint import pprint

# artifacts
import wet_bulb
import synopsis
import solar_rad_expected
import okta_funcs
import cumulus_comms

# import definitions
import get_cumulus_weather_info
import get_env
import get_env_app


# Add a bunch of reliability code to this before deploying

# use aercus value now I have it
# def get_light_level(uuid):
#     """
#     Read lux/watts levels from light sensor
#     """
#     query = {}                                  # API call to light-service
#     query['app_name'] = 'webcamd'
#     query['uuid'] = uuid
#
#     light_service_listen_port = 9503
#     light_service_endpoint_base = 'http://192.168.1.180:' + light_service_listen_port.__str__()
#
#     status_code, response_dict = call_rest_api.call_rest_api(light_service_endpoint_base + '/get_lux', query)
#
#     lux = response_dict['lux']
#     sky_condition = response_dict['sky_condition']
#     watts = round(response_dict['watts'], 2)
#
#     return int(lux), watts, sky_condition


def send_tweet(tweet_text, uuid):
    """
    Send a Tweet - i.e. not enough light etc, so just send the met info
    """
    try:
        query = {}                                  # API call to twitter-service
        query['app_name'] = 'webcamd'
        query['uuid'] = uuid
        query['tweet_text'] = tweet_text
        query['hashtag_arg'] = 'metminiwx'          # do not supply the #
        query['lat'] = 51.4151                      # FIXME - put in definitions.py Stockcross
        query['lon'] = -1.3776                      # Stockcross

        status_code, response_dict = cumulus_comms.call_rest_api(get_env.get_twitter_service_endpoint() + '/send_text', query)

        if response_dict['status'] == 'OK' :
            tweet_len = response_dict['tweet_len'].__str__()
            print('Tweet sent OK, tweet_len=' + tweet_len + ', uuid=' + uuid.__str__())
        else:
            print(response_dict['status'])

    except Exception as e:
        print('Error : ' + e.__str__())


def send_tweet_with_video(tweet_text, filename, uuid):
    """
    Send a Tweet with a video file
    """
    try:
        query = {}                                  # API call to twitter-service
        query['app_name'] = 'webcamd'
        query['uuid'] = uuid
        query['tweet_text'] = tweet_text
        query['hashtag_arg'] = 'metminiwx'          # do not supply the #
        query['lat'] = 51.4151                      # Stockcross
        query['lon'] = -1.3776                      # Stockcross
        query['video_pathname'] = filename

        status_code, response_dict = cumulus_comms.call_rest_api(get_env.get_twitter_service_endpoint() + '/send_video', query)

        # print('status_code=' + status_code.__str__())
        # pprint(response_dict)
        # if response_dict['status'] == 'OK' and response_dict['tweet_sent'] == True:
        if response_dict['status'] == 'OK' :
            tweet_len = response_dict['tweet_len'].__str__()
            print('Tweet sent OK, tweet_len=' + tweet_len + ', uuid=' + uuid.__str__())
        else:
            print(response_dict['status'])

    except Exception as e:
        print('Error : ' + e.__str__())


def main():
    try:
        crf = 19                                # H264 encoding quality parameter
        my_app_name = 'webcamd'
        version = get_env.get_version()
        verbose = get_env.get_verbose()
        stage = get_env.get_stage()
        cumulusmx_endpoint = get_env.get_cumulusmx_endpoint()
        webcam_service_endpoint = get_env.get_webcam_service_endpoint()

        video_length_secs = get_env_app.get_video_length()
        preamble_secs = get_env_app.get_video_preamble()
        min_solar = get_env_app.get_min_solar()
        max_solar = get_env_app.get_max_solar()
        mins_between_videos = get_env_app.get_mins_between_videos()

        webcam_query = {}                       # API call to webcam-service
        webcam_query['app_name'] = my_app_name
        webcam_query['video_length_secs'] = video_length_secs
        webcam_query['preamble_secs'] = preamble_secs

        lat = 51.4151  # Stockcross - move to artifact definitions
        lon = -1.3776  # Stockcross

        print(my_app_name + ' started, version=' + version)
        print('stage=' + stage)
        if stage == 'DEV':
            verbose = True
        print('verbose=' + verbose.__str__())
        print('webcam-service endpoint=' + webcam_service_endpoint)
        print('cumulusmx endpoint=' + cumulusmx_endpoint)
        print('twitter-service endpoint=' + get_env.get_twitter_service_endpoint())
        print('min_solar=' + min_solar.__str__())
        print('max_solar=' + max_solar.__str__())
        print('mins_between_videos=' + mins_between_videos.__str__())
        print('preamble_secs=' + preamble_secs.__str__())
        print('video_length_secs=' + video_length_secs.__str__())

        print('entering main loop...')
        while True:
            print(time.ctime() + ' : top of loop')
            this_uuid = str(uuid.uuid4())          # unique uuid per cycle
            try:
                cumulus_weather_info = get_cumulus_weather_info.get_key_weather_variables(cumulusmx_endpoint)     # REST API call
                if cumulus_weather_info is None:
                    print('Error: CumulusMX did not return valid data')
                    cumulus_comms.wait_until_cumulus_data_ok(cumulusmx_endpoint)             # loop until CumulusMX data is OK
                    continue                                                                # resume at the while()

                temp_c = float(cumulus_weather_info['OutdoorTemp'])
                pressure = float(cumulus_weather_info['Pressure'])
                dew_point_c = float(cumulus_weather_info['OutdoorDewpoint'])
                wet_bulb_c = wet_bulb.get_wet_bulb(temp_c, pressure, dew_point_c)
                rain_rate = float(cumulus_weather_info['RainRate'])
                wind_knots_2m = float(cumulus_weather_info['WindAverage'])
                solar = cumulus_weather_info['SolarRad']

                # common code with synopsisd
                altitude_deg = solar_rad_expected.calc_altitude(lat, lon)
                solar_radiation_theoretical = solar_rad_expected.get_solar_radiation_theoretical(altitude_deg)

                synopsis_code, synopsis_text = synopsis.get_synopsis(temp_c, wet_bulb_c, dew_point_c, rain_rate,
                                                                 wind_knots_2m, solar)
                if 'fog' in synopsis_text:
                    is_fog = True
                else:
                    is_fog = False

                # derived cloud coverage estimate
                cloud_coverage_percent = solar_rad_expected.calc_cloud_coverage(lat, lon, solar, solar_radiation_theoretical)
                okta = okta_funcs.coverage_to_okta(cloud_coverage_percent, is_fog)
                okta_text = okta_funcs.convert_okta_to_cloud_cover(okta)[0]

                # ' wmo4680=' + synopsis_code.__str__() + ' (' + synopsis_text + ')' + \
                # Tweet the video
                tweet_text = ' fcast *' + cumulus_weather_info['Forecast'] + '*' + \
                ', wind_chill=' + cumulus_weather_info['WindChill'].__str__() + cumulus_weather_info['TempUnit'] + \
                ', wind=' + cumulus_weather_info['Beaufort'].__str__() + \
                ' (max=' + cumulus_weather_info['HighBeaufortToday'].__str__() + ')' + \
                ', ' + cumulus_weather_info['DominantWindDirection'] + \
                ', cbase=' + cumulus_weather_info['Cloudbase'].__str__() + ' ' + cumulus_weather_info['CloudbaseUnit'] + \
                ', ' + cumulus_weather_info['Pressure'].__str__() + ' ' + cumulus_weather_info['PressUnit'] + \
                ', trend=' + cumulus_weather_info['PressTrend'].__str__() + \
                ', temp=' + cumulus_weather_info['OutdoorTemp'].__str__() + cumulus_weather_info['TempUnit'] + \
                ', Twb=' + wet_bulb_c.__str__() + cumulus_weather_info['TempUnit'] + \
                ', Tdp=' + cumulus_weather_info['OutdoorDewpoint'].__str__() + cumulus_weather_info['TempUnit'] + \
                ', last_rain=' + cumulus_weather_info['LastRainTipISO'] + \
                ', rain_rate=' + cumulus_weather_info['RainRate'].__str__() + \
                ', rain_today=' + cumulus_weather_info['RainToday'].__str__()
                # ', solar=' + cumulus_weather_info['SolarRad'].__str__()

                tweet_text = ' Stockcross, UK : fcast *' + cumulus_weather_info['Forecast'] + '*' + \
                         ', wmo4680=' + synopsis_code.__str__() + ' (' + synopsis_text + ')' + \
                         ', temp=' + temp_c.__str__() + \
                         ', solar=' + solar.__str__() + \
                         ', okta=' + okta.__str__() + ' (' + okta_text + ')'
                print(tweet_text)

                if solar < float(min_solar) or solar > float(max_solar):                  # do not bother taking video if it is too dark
                    send_tweet(tweet_text, this_uuid)
                else:
                    webcam_query['uuid'] = this_uuid.__str__()
                    print('Requesting webcam mp4 video and a jpg from webcam-service, uuid=' + this_uuid.__str__() + ' ...')
                    status_code, response_dict = cumulus_comms.call_rest_api(get_env.get_webcam_service_endpoint() + '/get_video', webcam_query)
                    pprint(response_dict)

                    # if response_dict['status'] != 'OK':
                    #     print(response_dict['status'] + ', sleeping for 2 mins...')
                    #     time.sleep(120)
                    #     continue    # go back to start of infinite loop

                    # Video/image grabbed OK
                    mp4_filename = response_dict['video_filename']
                    jpeg_filename = response_dict['jpeg_filename']

                    print('wrote webcam video to : ' + mp4_filename.__str__() + ', uuid=' + this_uuid)
                    print('wrote webcam jpeg to  : ' + jpeg_filename.__str__() + ', uuid=' + this_uuid)

                    if '/' in mp4_filename:
                        filename = mp4_filename.split('/')[-1]          # ignore the filepath
                        tweet_text = tweet_text + ' ' + filename
                        send_tweet_with_video(tweet_text, mp4_filename, this_uuid)
                    else:
                        print('Error : mp4_filename=' + mp4_filename.__str__())
                        raise()

            except Exception as e:
                print('Error in main loop : ' + e.__str__())
                print('status_code=' + status_code.__str__())
                pprint(response_dict)
                print('Backoff sleeping...')
                time.sleep(5 * 60)
                print('back to top of loop')
                continue            # just have another attempt...

            sleep_secs = mins_between_videos * 60
            print('----------------------------------------------')
            print(time.ctime() + ' : sleeping for ' + sleep_secs.__str__() + ' seconds...')
            time.sleep(sleep_secs)

    except Exception as e:
        print('Fatal error : ' + e.__str__())
        traceback.print_exc()


if __name__ == '__main__':
    main()


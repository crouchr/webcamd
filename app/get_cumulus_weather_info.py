import call_rest_api
from pprint import pprint


def get_key_weather_variables():
    """
    Get some critical weather variables by querying the CumumlusMX REST API
    """

    endpoint = 'http://192.168.1.180:8998/api/data/currentdata'

    status_code, response_dict = call_rest_api.call_rest_api(endpoint, None)
    # print('status_code=' + status_code.__str__())
    #pprint(response_dict)

    if status_code == 200:
        return response_dict
    else:
        return None

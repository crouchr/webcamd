import call_rest_api
import definitions
from pprint import pprint


def get_key_weather_variables():
    """
    Get some critical weather variables by querying the CumumlusMX REST API
    """

    endpoint = definitions.cumulusmx_endpoint

    status_code, response_dict = call_rest_api.call_rest_api(endpoint, None)
    # print('status_code=' + status_code.__str__())
    #pprint(response_dict)

    if status_code == 200:
        return response_dict
    else:
        return None

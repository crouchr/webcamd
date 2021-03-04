import cumulus_comms
from pprint import pprint


def get_key_weather_variables(cumulus_endpoint):
    """
    Get some critical weather variables by querying the CumulusMX REST API
    """

    status_code, response_dict = cumulus_comms.call_rest_api(cumulus_endpoint, query=None)

    # Aercus to CumulusMX serial connection down - all data now invalid
    if status_code == 200 and response_dict['DataStopped'] :
        return None

    # print('status_code=' + status_code.__str__())
    #pprint(response_dict)

    if status_code == 200:
        return response_dict
    else:
        return None

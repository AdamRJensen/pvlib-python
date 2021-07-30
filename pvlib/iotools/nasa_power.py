import os
import json
import requests
import pandas as pd

# Add more outputformats to documentation or just to an admonition box
# climatology, monthly, daily, hourly


NASA_POWER_URL = r"https://power.larc.nasa.gov/beta/api/"

NASA_POWER_VARIABLE_MAP = {}

def get_nasa_power(latitude, longitude, start, end, parameters,
                   time_step='hourly', outputformat='json', timeout=30):
    """Get solar radiation and meteorological data from NASA POWER.



    latitude: float
        In decimal degrees, between -90 and 90, north is positive (ISO 19115)
    longitude: float
        In decimal degrees, between -180 and 180, east is positive (ISO 19115)
    start: datetime-like
        First day of the time series.
    end: datetime-like
        Last day of the time series.
    paramters: list or tuple
        List of requested parameters.
    time_step: str, default: 'hourly'
        Temporal resolution of requested data. Must be in ['hourly', 'daily',
        'monthly', 'climateology']
    outputformat: str, default: 'json'
        Must be in ``['json', 'csv', 'ASCII', ]``. See NSASA POWER hourly data
        documentation [2]_ for more info.
    map_variables: bool, default: True
        When true, renames columns of the Dataframe to pvlib variable names
        where applicable. See variable NASA_POWER_VARIABLE_MAP.
    timeout: int, default: 30
        Time in seconds to wait for server response before timeout

    Returns
    -------
    data : pandas.DataFrame
        Time-series of hourly data, see Notes for fields
    inputs : dict
        Dictionary of the request input parameters
    metadata : dict
        Dictionary containing metadata

    Raises
    ------
    requests.HTTPError
        If the request response status is ``HTTP/1.1 400 BAD REQUEST``, then
        the error message in the response will be raised as an exception,
        otherwise raise whatever ``HTTP/1.1`` error occurred

    References
    ----------
    .. [1] `NASA POWER Docs <https://power.larc.nasa.gov/beta/docs/>`_
    .. [2] `NASA POWER Solar Data Overview <https://power.larc.nasa.gov/beta/docs/methodology/solar/>`_
    """
    params = {
        'parameters': ','.join(parameters),
        'community': 'RE',
        'longitude': longitude,
        'latitude': latitude,
        'start': start.strftime('%Y%m%d'),
        'end': end.strftime('%Y%m%d'),
        'format': outputformat}

    res = requests.get(NASA_POWER_URL + f"temporal/{time_step}/point",
                       params=params, timeout=timeout)

    # NASA POWER returns really well formatted error messages in JSON for
    # HTTP/1.1 400 BAD REQUEST so try to return that if possible, otherwise
    # raise the HTTP/1.1 error caught by requests
    if not res.ok:
        try:
            err_msg = res.json()
        except Exception:
            res.raise_for_status()
        else:
            raise requests.HTTPError(err_msg['Messages'])

    data = pd.DataFrame(res.json().pop('properties')['parameter'])
    data.index = pd.to_datetime(data.index, format='%Y%m%d')
    meta = res.json()

    return data, meta

parameters = ['T2M', 'T2MDEW', 'T2MWET', 'TS']

data, meta = get_nasa_power(latitude, longitude, start, end, parameters, time_step='daily')




# %%
locations = [(32.929, -95.770), (5, 10)]

parameters = ['T2M', 'T2MDEW', 'T2MWET', 'TS', 'T2M_RANGE', 'T2M_MAX', 'T2M_MIN']

outputformat = 'json'
start = pd.Timestamp(2020,1,1)
end = pd.Timestamp(2020,1,5)
latitude = 55
longitude = 10


params = {
    'parameters': ','.join(parameters),
    'community': 'RE',
    'longitude': longitude,
    'latitude': latitude,
    'start': start.strftime('%Y%m%d'),
    'end': end.strftime('%Y%m%d'),
    'format': format}

output = r""

for latitude, longitude in locations:
    api_request_url = base_url.format(longitude=longitude, latitude=latitude)

    response = requests.get(url=NASA_POWER_URL, verify=True, timeout=30.00)

    content = json.loads(response.content.decode('utf-8'))
    filename = response.headers['content-disposition'].split('filename=')[1]

    filepath = os.path.join(output, filename)
    with open(filepath, 'w') as file_object:
        json.dump(content, file_object)
    
# %%

data = json.load(open(filepath))
df = pd.DataFrame(data.pop('properties')['parameter'])

meta = data

# %%



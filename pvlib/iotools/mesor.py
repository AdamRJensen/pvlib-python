"""Functions to read data MESOR data files.
.. codeauthor:: Adam R. Jensen<adam-r-j@hotmail.com>
"""

import pandas as pd


MESOR_VARIABLE_MAP = {
    't_air': 'temp_air', 'rh': 'relative_humidity', 'ws': 'wind_speed',
    'wd': 'wind_direction', 'bp': 'air_pressure', 'GHI': 'ghi', 'DNI': 'dni',
    'DHI': 'dhi'}


def read_mesor(filename, map_variables=True):
    """
    Read a MESOR data file into a pandas DataFrame.

    The data format was developed as part of the MESOR project [1]_. The format
    is documented in [2]_.

    Parameters
    ----------
    filename: str or path-like
        Filename of a MESOR data file.
    map_variables: bool, default: True
        When true, renames columns of the Dataframe to pvlib variable names
        where applicable. See variable MESOR_VARIABLE_MAP.

    Returns
    -------
    data: pandas.DataFrame
        Timeseries data, see Notes for columns
    meta: dict
        Metadata from the data file

    Notes
    -----
    The returned data DataFrame includes the following fields:

    ========================  ======  =========================================
    Key, mapped key           Format  Description
    ========================  ======  =========================================
    *Mapped field names are returned when the map_variables argument is True*
    ---------------------------------------------------------------------------
    date                      str     Date of time period
    time                      str     Local time (see metadata for UTC offset)
    ghi                       float   Global horizontal irradiance (W/m^2)
    dni                       float   Direct normal irradiance (W/m^2)
    dhi                       float   Diffuse horizontal irradiance (W/m^2)
    t_air, temp_air           float   Air temperature (deg C)
    rh, relative_humidity     float   Relative humidity (%)
    bp, air_pressure          float   Air pressure (hPa)
    ws, wind_speed            float   Wind speed (m/s)
    wd, wind_direction        float   Wind direction (degrees)
    wd_var                    float   Variance of wind direction (degrees)
    ws_gust                   float   Wind gust speed (m/s)
    ========================  ======  =========================================


    Variables corresponding to standard pvlib variables are renamed,
    e.g. `ws` becomes `wind_speed`. See the
    `pvlib.iotools.cams.MESOR_VARIABLE_MAP` dict for the complete mapping.

    See Also
    --------
    pvlib.iotools.parse_mesor

    References
    ----------
    .. [1] `MESOR project website
       <http://www.mesor.org/>`_
    .. [1] `MESOR Deliverable 1.1.2 Existing Ground Data Sets
       <http://www.mesor.org/docs/MESoR_D1.1.2_ExistingGroundData_v1.0.pdf>`_
    """
    with open(filename, 'r') as fbuf:
        content = parse_mesor(fbuf, map_variables=map_variables)
    return content


def parse_mesor(fbuf, map_variables=True):
    """
    Parse a file-like buffer with data in the MESOR data format.
    
    The MESOR data format is described in [1]_.

    Parameters
    ----------
    fbuf: file-like object
        File-like object containing data to read.
    map_variables: bool, default: True
        When true, renames columns of the Dataframe to pvlib variable names
        where applicable. See variable MESOR_VARIABLE_MAP.

    Returns
    -------
    data: pandas.DataFrame
        Timeseries data
    meta: dict
        Metadata available in the file.

    See Also
    --------
    pvlib.iotools.read_mesor

    References
    ----------
    .. [1] `MESOR Deliverable 1.1.2 Existing Ground Data Sets
       <http://www.mesor.org/docs/MESoR_D1.1.2_ExistingGroundData_v1.0.pdf>`_
    """
    names = []  # Initialize list of column names
    meta = {'IPR': {}, 'location': {}, 'spectral': {}, 'comments': [],
            'timezone': {}, 'instruments': {}, 'channels': {}}
    meta['format'] = fbuf.readline().rstrip('\n').lstrip('#')
    # Parse through initial metadata section (lines starting with #)
    while True:
        line = fbuf.readline().rstrip('\n')
        if line.startswith('#comment -'):  # ignore metadata header lines
            continue
        elif line.startswith('#IPR'):
            meta['IPR'][line.split()[0].replace('#IPR.', '')] = \
                ' '.join(line.split()[1:])
        elif line.startswith('#timezone'):
            meta['timezone'] = line.split()[1]
        elif line.startswith('#location'):
            meta['location'][line.split('.')[1].split()[0].replace(':', '')] =\
                line.split()[1]
        elif line.startswith('#spectral'):
            meta['spectral'][line.split('.')[1].split()[0]] = \
                ' '.join(line.split()[1:])
        # Channels are in the order they appear in the data section
        elif line.startswith('#channel'):
            meta['channels'][line.split()[1]] = ' '.join(line.split()[2:])
            names.append(line.split()[1])
        elif line.startswith('#comment instrument'):
            instrument_id = line.split()[2]
            instrument_param = ' '.join(line.split()[3:]).split(':')[0]
            if instrument_id not in meta['instruments'].keys():
                meta['instruments'][instrument_id] = {}
            # depending on param, convert value to int or float
            param_value = ' '.join(':'.join(line.split(':')[1:]).split())
            if instrument_param in ['mult_cc', 'off_cc', 'sensitivity']:
                param_value = float(param_value)
            meta['instruments'][instrument_id][instrument_param] = param_value
        elif line.startswith('#comment'):
            meta['comments'].append(' '.join(line.split()[1:]))
        elif line.startswith('#begindata'):
            # The last line of the meta-data section contains the column names
            break  # End of meta-data section has been reached

    data = pd.read_csv(fbuf, header=None, names=names, delim_whitespace=True,
                       comment='#', na_values=[-9999, -999.9])
    # Set datetime as index
    data.index = pd.to_datetime(data['date'] + ' ' + data['time'])
    # Convert timezone to Pandas format, e.g. UTC-2 is converted to Etc/GMT+2
    if meta['timezone'] != 'TST':  # Cannot lozalize true solar time
        tz = meta['timezone'].replace('UTC+', 'Etc/GMT+')\
                             .replace('UTC-', 'Etc/GMT-')
        data.index = data.index.tz_localize(tz)  # Localize time series
        data = data.drop(columns=['date', 'time'])  # Drop date & time columns

    if map_variables:  # Map variable names to pvlib names
        data = data.rename(columns=MESOR_VARIABLE_MAP)
    return data, meta
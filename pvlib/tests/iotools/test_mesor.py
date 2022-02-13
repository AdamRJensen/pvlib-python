"""
tests for :mod:`pvlib.iotools.mesor`
"""

import pandas as pd
import numpy as np
import pytest
from pvlib.iotools import read_mesor
from ..conftest import DATA_DIR, assert_index_equal, assert_frame_equal


@pytest.fixture
def expected_index():
    index = pd.date_range(start='2005-2-1 01', periods=23, freq='1h', tz='UTC')
    index.freq = None
    return index

expected_data = [[np.nan, np.nan, np.nan, 0.0], [np.nan, np.nan, np.nan, 0.0],
                 [np.nan, np.nan, np.nan, 34.0],
                 [np.nan, np.nan, np.nan, 14.0],
                 [np.nan, np.nan, np.nan, 12.0], [0.0, 0.0, 0.0, 64.0],
                 [0.0, 0.0, 0.0, 120.0], [8.5, 0.0, 8.2, 120.0],
                 [37.9, 2.2, 35.2, 120.0], [98.3, 5.2, 92.8, 120.0],
                 [125.3, 11.2, 113.5, 120.0], [157.6, 20.1, 138.2, 120.0],
                 [242.8, 74.3, 167.7, 120.0], [128.2, 6.5, 122.2, 120.0],
                 [101.2, 18.6, 81.8, 120.0], [32.3, 2.7, 29.3, 120.0],
                 [4.7, 0.0, 4.4, 114.0], [0.0, 0.0, 0.0, 78.0],
                 [np.nan, np.nan, np.nan, 22.0],
                 [np.nan, np.nan, np.nan, 10.0],
                 [np.nan, np.nan, np.nan, 38.0], [0.0, 0.0, 0.0, 84.0],
                 [np.nan, np.nan, np.nan, np.nan]]

expected_columns = ['GHI', 'DNI', 'DHI', 'NoMV']


@pytest.fixture
def expected_dataframe(expected_index):
    return pd.DataFrame(data=expected_data, index=expected_index,
                        columns=expected_columns)


def test_read_mesor(expected_dataframe):
    data, meta = read_mesor(DATA_DIR / 'mesor_test_file.csv',
                            map_variables=False)
    assert_frame_equal(expected_dataframe, data)


def test_read_mesor_map_variables(expected_index):
    data, meta= read_mesor(DATA_DIR / 'mesor_test_file.csv',
                           map_variables=True)
    assert_index_equal(expected_index, data.index)
    assert 'GHI' not in data.columns
    assert 'ghi' in data.columns
    assert 'dhi' in data.columns
    assert 'dni' in data.columns

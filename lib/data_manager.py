# -*- coding: utf-8 -*-
"""Set of routines to manage input data for retrieve and convert
datasets Climatologic Database from the National Meteorological Service
of Mexico (SMN).
"""
__author__ = 'Roberto A. Real-Rangel (Institute of Engineering UNAM; Mexico)'
__license__ = 'GNU General Public License'

from collections import OrderedDict
import datetime as dt
import io
import numpy as np

from pathlib2 import Path
import toml
import xarray as xr


class Configurations():
    """
    """
    def __init__(self, config_file):
        self.config_file = config_file

        with open(self.config_file, 'rb') as file_content:
            config = toml.load(file_content)

        for key, value in config.items():
            setattr(self, key, value)


def list_inputs(input_dir, extension):
    return(sorted(list(Path(input_dir).glob(pattern='**/*' + extension))))


def read_bdcn_file(input_file):
    """Extracts data from files from the National Climatologic Data
    Base (BDCN) of Mexico.

    Parameters
    ----------
        input_file: string
            The full path of the input file of the climatological records.
    """
    # Import CSV file.
    with io.open(str(input_file), 'r', encoding='latin1') as f:
        raw_text = f.read().splitlines()

    # Separate header lines from data lines.
    separator = raw_text.index("---------- ------ ------ ------ ------")
    header = raw_text[:separator]
    data = raw_text[separator + 1:-1]

    # Process data rows.
    def flitem2array(input_list, item):
        return(np.array([
                np.nan if i == 'Nulo'
                else np.float32(i)
                for i in [row[item] for row in input_list]]))

    def parse_date(date_string, add_time=' 00:00'):
        """Convert date strings from DD/MM/YYYY format to YYYY-MM-DD
        format.

        It also adds " 08:00" to the string. This is due to the BDC
        datasets values are measured at 8:00 h."""
        return('-'.join(list(reversed(date_string.split('/')))) + add_time)

    data_stripped = [[i for i in row.split(' ') if i != ''] for row in data]
    dates = [np.datetime64(parse_date(date_string=row[0], add_time=' 08:00'))
             for row in data_stripped]
    prec = flitem2array(data_stripped, 1)
    evap = flitem2array(data_stripped, 2)
    tmax = flitem2array(data_stripped, 3)
    tmin = flitem2array(data_stripped, 4)
    dataset = xr.Dataset(
            data_vars={'prec': (['time'], prec),
                       'evap': (['time'], evap),
                       'tmax': (['time'], tmax),
                       'tmin': (['time'], tmin)},
            coords={'time': dates})

    # Remove repeated dates.
    # !!! If a date appears more than one time in the record, only the
    # !!! first one is retained.
    _, index = np.unique(dataset['time'], return_index=True)
    dataset = dataset.isel(time=index)

    # Reindex to fill missing dates with nan.
    if len(dates) > 0:
        new_index = np.arange(
                min(dates), max(dates) + np.timedelta64(1, 'D'),
                np.timedelta64(1, 'D'))
        dataset = dataset.reindex(time=new_index)

    # Process header rows.
    def retrieve_metadata(header, attr):
        attributes = [i.split(":") for i in header if len(i.split(":")) == 2]
        key = [i[0].strip() for i in attributes]
        val = [i[1].strip() for i in attributes]
        return(dict(zip(key, val))[attr])

    metadata = OrderedDict()
    metadata['Title'] = header[1].strip().title()
    metadata['Author'] = header[0].strip()
    metadata['StationID'] = retrieve_metadata(header, u'ESTACIÓN').zfill(5)
    metadata['StationName'] = retrieve_metadata(header, u'NOMBRE').title()
    metadata['State'] = retrieve_metadata(header, u'ESTADO').title()
    metadata['Municipality'] = retrieve_metadata(header, u'MUNICIPIO').title()
    metadata['Operability'] = (
            'Working'
            if retrieve_metadata(header, u'SITUACIÓN') == 'OPERANDO'
            else 'Not working')
    metadata['Owner'] = retrieve_metadata(header, u'ORGANISMO')
    metadata['WMOID'] = ("" if retrieve_metadata(header, u'CVE-OMM') == 'Nulo'
                         else retrieve_metadata(header, u'CVE-OMM'))
    metadata['Latitude'] = float(retrieve_metadata(header, u'LATITUD')[:-1])
    metadata['Longitude'] = float(retrieve_metadata(header, u'LONGITUD')[:-1])
    metadata['Elevation'] = float(
            retrieve_metadata(
                    header, u'ALTITUD').split(' ')[0].replace(',', ''))
    metadata['TemporalRange'] = (
            str(min(dates)) + " -> " + str(max(dates))
            if len(dates) > 0
            else "Empty dataset")
    metadata['TemporalResolution'] = (
            'Daily (08:00 of the past day - 08:00 of the current day; '
            'local time)')
    metadata['ProductionDateTime'] = "Original file generated on " + str(
            np.datetime64(parse_date(retrieve_metadata(header, u'EMISIÓN'))))
    metadata['Comment'] = (
            'Converted to NetCDF format on '
            + dt.datetime.now().isoformat()
            + ' by R. A. Real-Rangel (IIUNAM; rrealr@iingen.unam.mx)')
    metadata['Format'] = 'NetCDF-4/HDF-5'
    metadata['Version'] = '1.0.0'

    # Assigning attributes to xr.Dataset and xr.DataArrays
    dataset.attrs = metadata
    prec_attrs = OrderedDict()
    prec_attrs['long_name'] = 'Total_precipitation'
    prec_attrs['units'] = 'mm'
    dataset.prec.attrs = prec_attrs
    evap_attrs = OrderedDict()
    evap_attrs['long_name'] = 'Total_evaporation'
    evap_attrs['units'] = 'mm'
    dataset.evap.attrs = evap_attrs
    tmax_attrs = OrderedDict()
    # OPTIMIZE: v1.0.1 -- > Replace 'Maximum_temperature_in_the_last_24_hours'
    # OPTIMIZE: v1.0.1 -- > with 'Maximum_temperature'.
    tmax_attrs['long_name'] = 'Maximum_temperature_in_the_last_24_hours'
    tmax_attrs['units'] = 'C'
    dataset.tmax.attrs = tmax_attrs
    tmin_attrs = OrderedDict()
    # OPTIMIZE: v1.0.1 -- > Replace 'Minimum_temperature_in_the_last_24_hours'
    # OPTIMIZE: v1.0.1 -- > with 'Minimum_temperature'.
    tmin_attrs['long_name'] = 'Minimum_temperature_in_the_last_24_hours'
    tmin_attrs['units'] = 'C'
    dataset.tmin.attrs = tmin_attrs
    return(dataset)

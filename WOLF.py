#_*_ coding:utf-8-*-
import sys
import os
import gdal
import h5py
from netCDF4 import Dataset
import xarray as xr


data = Dataset("C:/Users/30494/Desktop/wrfout_d01_2020-08-20_08_00_00/wrfout_d01_2020-08-20_08_00_00.nc", 'r')
outfile = "C:/Users/30494/Desktop/wrfout_d01_2020-08-20_08_00_00/test.hdf"

dzs = data['DZS']
SMOIS = data['SMOIS']
XLONG = data['XLONG']
XLAT = data['XLAT']

ds = xr.Dataset(
    {
        'DZS':(['Time','soil_layers_stag'],dzs),
        
        'SMOIS':(['Time', 'soil_layers_stag', 'south_north', 'west_east'],SMOIS)
        },

        coords = {
                'lon':(['Time','south_north','west_east'],XLONG),
                'lat':(['Time','south_north','west_east'],XLAT)
                }
)

ds.to_netcdf("C:/Users/30494/Desktop/wrfout_d01_2020-08-20_08_00_00/test.nc")

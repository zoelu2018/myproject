import h5py
from netCDF4 import Dataset 
import os
import xarray as xr
class H5file(object):
    def __init__(self,filename):
        self.filename = filename
        try:
            self.hdf_handle = h5py.File(filename,'r')
        except BaseException as e:
            raise e
    def get_attribute(self):

        return  list(self.hdf_handle.attrs.keys()),list(self.hdf_handle.attrs.values())
    def get_group(self):

        return list(self.hdf_handle.keys())
    def get_member(self):

        return list(self.hdf_handle.values())
class NCfile(object):
    def __init__(self,filename):
        self.filename = filename
        try:
            self.nc_handle = xr.open_dataset(filename)
        except BaseException as e:
            raise e
    def get_attribute(self):

        return  self.nc_handle.attrs

if __name__ =='__main__':

    infilepath = 'C:/Users/30494/Desktop/testtif/FY3D_MERSI_GBAL_L1_20201128_0730_GEO1K_MS.HDF'

    type = os.path.splitext(infilepath)[1]
    if type == '.HDF':
        dta = H5file(infilepath)
        keys,values  = dta.get_attribute()
        groups = dta.get_group()
        members = dta.get_member()
        for i in range(0,len(members)):
            subdta = list(members[i].values())
            for j in range(0,len(subdta)):
                sub_keys,sub_values = subdta[j].attrs.keys(),subdta[j].attrs.values()
    elif type == '.NC' or type == '.nc':
        dta = NCfile(infilepath)
        Attrs  = dta.get_attribute()  # 全局的属性
        groups = dta.nc_handle.data_vars
        for i in groups:
            attrs = dta.nc_handle[i].attrs  #单个数据的属性
        lat_a = dta.nc_handle.coords.variables.mapping['lat'].attrs #经纬度信息
        lon_a = dta.nc_handle.coords.variables.mapping['lon'].attrs 



            






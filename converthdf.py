import h5py
#from pyhdf import SD
import numpy as np
import time
import datetime
import sys
import os
def WriteData(NVI,strname,sdsname):
    NVI_INFO = h5py.File(NVI, 'r')
    data = NVI_INFO['NVI'].value
    dirs = os.path.dirname(strname)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    data = np.array(data)
    size = data.shape
    type = data.dtype
    #读取NVI的属性信息传递给ANPP
    res = NVI_INFO.attrs['Latitude Precision']
    Max_Lat = NVI_INFO.attrs['Maximum Latitude']
    Max_Lon = NVI_INFO.attrs['Maximum Longitude']
    Min_Lat = NVI_INFO.attrs['Minimum Latitude']
    Min_Lon = NVI_INFO.attrs['Minimum Longitude']
    data_date = NVI_INFO.attrs['Data Date']
    fout = h5py.File(strname, "w")
    fout.attrs['Data Date'] = data_date
    fout.attrs['File Name'] = strname
    fout.attrs['Latitude Precision'] = res
    fout.attrs['Longitude Precision'] = res
    fout.attrs['Maximum Latitude'] = Max_Lat
    fout.attrs['Maximum Longitude'] = Max_Lon
    fout.attrs['Maximum X'] = Max_Lon
    fout.attrs['Maximum Y'] = Max_Lat
    fout.attrs['Minimum Latitude'] = Min_Lat
    fout.attrs['Minimum Longitude'] = Min_Lon
    fout.attrs['Minimum X'] = Min_Lon
    fout.attrs['Minimum Y'] = Min_Lat
    fout.attrs['Orbit Direction'] = 'A'
    fout.attrs['Piexl Height'] = size[0]
    fout.attrs['Piexl Width'] = size[1]
    fout.attrs['Product Name '] = 'ANPP'    
    dset = fout.create_dataset(name=sdsname, shape=size, dtype='int16', data=data,compression="gzip", compression_opts=7)
    # for key in data.attrs.keys():
    #     dset.attrs[key] = data.attrs[key]
    fout.close()
if __name__ == '__main__':
     WriteData('D:/work/leimeng/TERRA_MODIS_Latlon_L3_NVI_MAX_20190701000000_20190731235959_0250M_POAM_D.HDF','D:/work/leimeng/test.HDF','test')
#-*- coding:utf-8 -*- 
# import gdal
import h5py
import os 
import sys
import numpy as np
from HDF2TIFF import tiff
def convert(input,output):
    img = h5py.File(input,'r')
    data =img['EVB1040'].value
    tiff(data)
if __name__ == '__main__':
    convert('D:/work/FY4/fy4AMV/FY4A-_AGRI--_N_DISK_1047E_L2-_PRD-_MULT_GLL_20201105010000_20201105011459_4000M_VPRJ5.HDF','D:/work/FY4/fy4AMV/test/')

    


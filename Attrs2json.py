#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import h5py
import os
import json
import numpy as np
from  netCDF4 import Dataset

def Formatdta(value):

    if isinstance(value, np.ndarray):
        if len(value) == 1:
            value = float(value[0])
        else:
            value = value.tolist()
    elif  isinstance(value,np.uint16) or isinstance(value,np.float32):
        value = value.tolist()
    else:
        value = value

    return value



def output(Infile,global_attrs,dataset_attrs):

    filename = os.path.basename(Infile)
    out_file = {
        filename : global_attrs,
        'dataset':dataset_attrs
    }
    item = json.dumps(out_file)

    outpath = Infile+'.json'
    try:
        if not os.path.exists(outpath):
            with open(outpath, "w") as f:
                # f.write(item + ",\n")
                f.write(item + "\n")
                print("^_^ write success")
        else:
            with open(outpath, "a") as f:
                # f.write(item + ",\n")
                f.write(item + "\n")
                print("^_^ write success")
    except Exception as e:
        print("write error==>", e)
def H5FILE_ATTRTS(Infile):
    dta = h5py.File(Infile,'r')
    globalattrs = dict(dta.attrs)

    global_attrs ={}
    dataset_attrs = {}
    #全局属性
    for key in globalattrs.keys():

        value_ = globalattrs[key]

        value = Formatdta(value_)
        global_attrs.update({key:value})

    member = dta.keys()
    # 数据集属性
    for m in member:

        subattrs = dict(dta[m].attrs)

        dtattrs = {}

        dataset_attrs[m] = dtattrs
        for subkey in subattrs.keys():
            subvalue_ = subattrs[subkey]
            subvalue = Formatdta(subvalue_)
            dtattrs.update({subkey:subvalue})
    output(infilepath,global_attrs,dataset_attrs)

def NCFILE_ATTRTS(infilepath):

    dta = Dataset(infilepath,'r')
    #全局变量
    global_attrs = {}
    for key in dta.ncattrs():
        value_ = getattr(dta,key)
        value = Formatdta(value_)
        global_attrs.update({key:value})
    member = list(dta.variables)
    dataset_attrs = {}
    # 数据集 属性
    for subkey in member:
        print(subkey)
        subattr = dta.variables[subkey]
        dtattrs = {}
        dataset_attrs[subkey] = dtattrs
        for sub_key in subattr.ncattrs():
            value_ = getattr(subattr,sub_key)
            print(value_)
            subvalue = Formatdta(value_)
            dtattrs.update({sub_key:subvalue})
    output(infilepath,global_attrs,dataset_attrs)
if __name__ =='__main__':

    infilepath = 'C:/Users/30494/Desktop/testtif/FY3D_MERSI_Latlon_L2_LST_NULL_20200831000000_20200831000000_1000M_POAI_D.HDF'

    type = os.path.splitext(infilepath)[1]

    if type == '.HDF' or type == '.hdf':
        H5FILE_ATTRTS(infilepath)
    if type == '.NC' or type == '.nc':
        NCFILE_ATTRTS(infilepath)
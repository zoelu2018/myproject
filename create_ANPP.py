#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   create_ANPP.py
@Time    :   2020/09/17 11:04:45
@Author  :   luxiaolin
@Version :   python-2.7.18,64bit
@Contact :   newbie2019@qq.com
'''

import sys
import os
import pandas as pd
import h5py
import numpy as np
import numpy.ma as npm
from sklearn import linear_model
import gdal
import osr
import pandas as pd
from time import *
from sys import argv, stdout, stderr
import traceback


def read_excel(infile):

    df = pd.read_excel(infile)
    lat = df['Lat'].values
    lon = df['Lon'].values
    std = df['ANPP'].values
    return lat, lon, std


def read_hdf(lat, lon, image):

    hdf_file = h5py.File(image, 'r')

    data = hdf_file['NVI'].value
    res = hdf_file.attrs['Latitude Precision']
    lat_max = hdf_file.attrs['Maximum Latitude']
    lon_min = hdf_file.attrs['Minimum Longitude']
    # 获取站点数据的行列号
    ord = np.zeros((len(lon), 2), dtype=int)
    x, y = ord[:, 0], ord[:, 1]
    for i in range(len(lon)):
        x[i], y[i] = int((lon[i] - lon_min) / res), int((lat_max - lat[i]) / res)
    img_data = np.zeros(len(lon))
    for index in range(len(lon)):
        # 获取3x3网格的数据
        x_start = x[index] - 5
        y_start = y[index] - 5
        x_end = x[index] + 5
        y_end = y[index] + 5
        if x_start < 0 or x_end > 28001 or y_start < 0 or y_end > 24001:
            img_data = data[y[index], x[index]]
        else:
            dt = data[y_start:y_end, x_start:x_end]
            no_data_mask = dt >= 32002
            img_data[index] = np.mean(dt[~no_data_mask])
    return img_data, data


def WriteData(NVI, strname, sdsname, data):
    time11 = time()
    dirs = os.path.dirname(strname)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    size = data.shape
    # 读取NVI的属性信息传递给ANPP
    nvi_file = h5py.File(NVI, 'r')
    res = nvi_file.attrs['Latitude Precision']
    Max_Lat = nvi_file.attrs['Maximum Latitude']
    Max_Lon = nvi_file.attrs['Maximum Longitude']
    Min_Lat = nvi_file.attrs['Minimum Latitude']
    Min_Lon = nvi_file.attrs['Minimum Longitude']
    proj_str = nvi_file.attrs['Projection Type']
    data_date = nvi_file.attrs['Data Date']
    out_file = h5py.File(strname, "w")
    out_file.attrs['Data Date'] = data_date
    out_file.attrs['File Name'] = strname
    out_file.attrs['Latitude Precision'] = res
    out_file.attrs['Longitude Precision'] = res
    out_file.attrs['Maximum Latitude'] = Max_Lat
    out_file.attrs['Maximum Longitude'] = Max_Lon
    out_file.attrs['Maximum X'] = Max_Lon
    out_file.attrs['Maximum Y'] = Max_Lat
    out_file.attrs['Minimum Latitude'] = Min_Lat
    out_file.attrs['Minimum Longitude'] = Min_Lon
    out_file.attrs['Minimum X'] = Min_Lon
    out_file.attrs['Minimum Y'] = Min_Lat
    out_file.attrs['Orbit Direction'] = 'A'
    out_file.attrs['Piexl Height'] = size[0]
    out_file.attrs['Piexl Width'] = size[1]
    out_file.attrs['Product Name'] = 'ANPP'
    out_file.attrs['Projection Type'] = proj_str
    out_file.create_dataset(name=sdsname, shape=size, dtype='int16', data=data)
    out_file.close()
    return


def ANPP(input, img, output):
    stdout.write('$process|%d\n' % 3)
    stdout.flush()
    lat, lon, std = read_excel(input)
    img_data, data = read_hdf(lat, lon, img)
    stdout.write('$process|%d\n' % 10)
    stdout.flush()
    # 进行线性拟合
    xx = np.reshape(img_data, newshape=(len(img_data), 1))
    yy = np.reshape(std, newshape=(len(std), 1))
    reg = linear_model.LinearRegression(fit_intercept=True, normalize=False)
    reg.fit(xx, yy)
    k = reg.coef_  # 获取斜率w1,w2,w3,...,wn
    b = reg.intercept_  # 获取截距w0
    stdout.write('$process|%d\n' % 30)
    stdout.flush()
    xxx = xx.reshape(len(xx))
    yyy = yy.reshape(len(yy))
    g_s_m = pd.Series(xxx)
    g_a_d = pd.Series(yyy)
    corr_gust = round(g_s_m.corr(g_a_d), 4)
    stdout.write('$process|%d\n' % 50)
    stdout.flush()
    mask1 = data == 32002
    mask2 = data == 32767
    mask = (data == 32002) & (data == 32767)

    tar = np.ones((data.shape[0], data.shape[1]))
    tar[~mask] = (k[0] * data[~mask] + b)
    tar[mask1] = 32002
    tar[mask2] = 32767
    stdout.write('$process|%d\n' % 80)
    stdout.flush()

    result = WriteData(img, output, 'ANPP', tar)
    stdout.write('$process|%d\n' % 100)
    stdout.flush()
    stdout.write('$output|%s\n' % output)
    stdout.flush()
    return output


if __name__ == '__main__':
    # SITEPATH = sys.argv[1]
    # NVIFILE = sys.argv[2]
    # OUTFILE = sys.argv[3]
    # NVI数据必须是月数据，不然匹配不上站点数据,除去正常的库还用到了xlrd、sklearn库
    # SITEPATH = r'F:\\ZL\\data\\sitedata'
    # NVIFILE = r'F:\\ZL\\data\\TERRA_MODIS_Latlon_L3_NVI_MAX_20190401000000_20190430235959_0250M_POAM_D.HDF'
    # OUTFILE = r'F:\\ZL\\data\\guest\\MA218\\TERRA_MODIS_Latlon_L3_ANPP_MAX_20190401000000_20190430235959_0250M_POAM_D.HDF'
    # print SITEPATH, NVIFILE, OUTFILE
    # try:
    #     filename = os.path.basename(NVIFILE)
    #     filetime = filename.split('_')[6:8]
    #     stdname = os.path.join(SITEPATH, 'ANPP' + '_' + filetime[0] + '_' + filetime[1] + '.xlsx')
    #     outname = OUTFILE
    #     if os.access(stdname, os.F_OK):
    #         ANPP(stdname, NVIFILE, outname)
    #     else:
    #         stderr.write('$error| please input NVI POAM data and check the HDF if exists !!!  + ')
    #         stderr.flush()
    # except BaseException as e:
    #     stderr.write('$error|%s' % e + " at ANPP_P.py!!! " + ':' + traceback.format_exc())
    #     stderr.flush()
    #     sys.exit(2)
    std = r'D:/work/leimeng/'
    NVI = r'D:/work/leimeng/TERRA_MODIS_Latlon_L3_NVI_MAX_20190701000000_20190731235959_0250M_POAM_D.HDF'
    OUTPATH = r'D:/work/leimeng/'
    try: 
        filename = os.path.basename(NVI)
        filetime = filename.split('_')[6:8]
        stdname = os.path.join(std,'ANPP'+'_'+filetime[0]+'_'+filetime[1]+'.xlsx')
        outname = os.path.join(OUTPATH,filename.split('_')[0]+'_'+filename.split('_')[1]+'_'+filename.split('_')[2]+'_'+filename.split('_')[3]+'_ANPP_AVG_'+filetime[0]+'_'+filetime[1]+'_'+filename.split('_')[8]+'_POAM_X.HDF')
        if os.access(stdname, os.F_OK):
            ANPP(stdname,NVI,outname)
            print("程序完成--")
        else:
            print("站点数据不存在")
    except IOError as io_err:
        stderr.write('$error|%s' % io_err + " at ANPP_P.py!!! " + ':' + traceback.format_exc())
        stderr.flush()
        sys.exit(2) 

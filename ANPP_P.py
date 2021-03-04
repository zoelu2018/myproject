#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ANPP_P.py
@Time    :   2020/09/17 11:04:45
@Author  :   luxiaolin 
@Version :   python-2.7.18,64bit
@Contact :   newbie2019@qq.com
'''

# here put the import lib
import numpy
import sys
import os
import  pandas as pd
import h5py
import numpy as np
import numpy.ma as npm
from sklearn import linear_model
import gdal,osr
import pandas as pd
from time import *
from sys import argv, stdout, stderr
import traceback
# from hdfoper import HDFOper
# 打开excel文件，读取经纬度信息，以及站点数据
def read_excel(infile):
    # root_path = unicode(infile,'utf-8')
    try:
        df = pd.read_excel(infile)
        # df = pd.read_excel(infile)
        # head = df.head()
        # id = df ['ID'].values
        lat = df['Lat'].values
        lon = df['Lon'].values
        std = df['ANPP'].values
        return lat,lon,std
    except BaseException as e: # 读取excel文件失败
        print '读取源文件失败'
        return 11
def read_hdf(lat,lon,image):
    try:
        hdffile = h5py.File(image, 'r')
    except BaseException as e: # 读取源文件失败
        print '读取HDF文件失败'
        return 12
    data = hdffile['NVI'].value
    res = hdffile.attrs['Latitude Precision']
    lat_max = hdffile.attrs['Maximum Latitude']
    lon_min = hdffile.attrs['Minimum Longitude']
    #获取站点数据的行列号
    ord = np.zeros((len(lon),2),dtype = int)
    x,y = ord[:,0],ord[:,1]
    for i in range(len(lon)):
        x[i],y[i]=int((lon[i]-lon_min)/res) ,int((lat_max-lat[i])/res)
    imgdata = np.zeros(len(lon))
    for index in range(len(lon)):
        #获取3x3网格的数据 
        x_start = x[index]-5
        y_start = y[index]-5
        x_end = x[index]+5
        y_end = y[index]+5
        if x_start < 0 or x_end >28001 or y_start < 0 or y_end >24001:
            imgdata = data[y[index],x[index]]
        else:
            dt = data[y_start:y_end,x_start:x_end]
            nodatamask = dt >=32002
            imgdata[index] = np.mean(dt[~nodatamask])
            # print(imgdata[index])

    #    imgdata[index] = data[x[index],y[index]]
    return imgdata,data
def WriteData(NVI,strname,sdsname,data):
    time11 = time()
    dirs = os.path.dirname(strname)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    #data = np.array(data).astype(int)
    # print(data)
    size = data.shape
    #读取NVI的属性信息传递给ANPP
    NVI_INFO = h5py.File(NVI, 'r')
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
    fout.attrs['Product Name'] = 'ANPP'    
    dset = fout.create_dataset(name=sdsname, shape=size, dtype='int16', data=data,compression="gzip", compression_opts=1)
    # for key in data.attrs.keys():
    #     dset.attrs[key] = data.attrs[key]
    fout.close()
    time22 = time()-time11
    print('输出为HDF格式文件所用的时间为{}'.format(time22))
    return strname
def tif(data):
    im_geotrans= [70,0.0025,0,60,0,-0.0025] #左上角坐标，以及分辨率
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS('WGS84')
    im_proj = srs.ExportToWkt()
    row = data.shape[0]  # 行数
    col = data.shape[1]
    # d3 = np.reshape(d2,(721,1440))
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create('test_2019.07.tif', col, row, 1,gdal.GDT_Float32)
    dst_ds.SetProjection(im_proj)
    dst_ds.SetGeoTransform(im_geotrans)
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds.FlushCache()
def ANPP(input,img,output):
    begin_time = time()
    lat,lon,std = read_excel(input)
    imgdata , data= read_hdf(lat,lon,img)
    ###进行线性拟合
    xx =  np.reshape(imgdata,newshape=(len(imgdata),1))
    yy =  np.reshape(std,newshape=(len(std),1))
    reg=linear_model.LinearRegression(fit_intercept=True,normalize=False)
    reg.fit(xx,yy)
    k=reg.coef_#获取斜率w1,w2,w3,...,wn
    b=reg.intercept_#获取截距w0
    xxx = xx.reshape(len(xx))
    yyy = yy.reshape(len(yy))
    g_s_m = pd.Series(xxx)
    g_a_d = pd.Series(yyy)
    corr_gust = round(g_s_m.corr(g_a_d), 4)
    print('斜率{}，截距{},相关系数{}'.format(k,b,corr_gust))
    end_time_1 = time()
    time1 = end_time_1 - begin_time
    print('获取斜率所用时间为:{}'.format(time1))
    ####x0表示影像值，y0表示结果值
    # ny, nx = np.array(data ).shape 
    # data = data.reshape(1,nx*ny) 
    # nodatamask = data >=32002
    # x0 = npm.array(data, mask=nodatamask)
    mask1 = data == 32002
    mask2 = data == 32767
    mask = (data == 32002) & (data == 32767)
    end_time_2 = time()
    time2 = end_time_2 - begin_time
    print('计算mask所用时间为:{}'.format(time2))
    tar = np.ones((data.shape[0], data.shape[1]))
    tar[~mask] = k[0]*data[~mask]+b
    tar[mask1] = 32002
    tar[mask2] = 32767
    print(tar.shape)
    end_time_3 = time()
    time3 = end_time_3 - begin_time
    tif(tar)
    print('整个反计算的过程所用时间为:{}'.format(time3))
    # result = WriteData(img,output,'ANPP',tar)
    print ('该循环程序运行时间：{}'.format(run_time))
    # print(output)
    return output
if __name__ == '__main__':
    std = r'D:/work/leimeng/'
    NVI = r'D:/work/leimeng/TERRA_MODIS_Latlon_L3_NVI_MAX_20190401000000_20190430235959_0250M_POAM_D.HDF'
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
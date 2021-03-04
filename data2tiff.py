#-*- coding: UTF-8 
import sys
import os
import json
import csv
import struct
import pickle
import numpy as np
import gdal,osr
def opendat(filename,nx,ny,nz):
    # filename = opendat('D:/work/shamo/haiyang/202008040300_0p25_gfs.dat',1440,721,54)
    data = np.fromfile(filename,'b')#文件导入
    ds =  np.zeros((ny,nx,nz))
    for t in range(nz):        
        if t != 55:
            continue
        # t=t+1
        # pic = np.zeros((ny,nx))
        n = 721*1440
        tmp =  data[t* 721*1440*4  : (t + 1) * 721*1440*4]
        d2 = struct.unpack(str(n)+"f", tmp)
        d3 = np.reshape(d2,(721,1440))
        pic = np.zeros((ny,nx))
        # test = np.zeros((ny,nx))
        for i in range(720, -1, -1):#纵向翻转
            #  print(d3[i,:])
            pic[720-i,:]=d3[i,:]
        #定义空间参考
        # pic = pic[::2,::2]
        pic = np.round(pic,2)
        # tmpu = pic[:,0]
        # pic = np.column_stack((pic, tmpu))
        ####定义空间参考
        im_geotrans= [0,0.25,0,90,0,-0.25] #左上角坐标，以及分辨率
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS('WGS84')
        im_proj = srs.ExportToWkt()
        row = pic.shape[0]  # 行数
        columns =pic.shape[1]
        # d3 = np.reshape(d2,(721,1440))
        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create('D:/work/shamo/Contour/image/20200804_tmp_0_25d.tif', columns, row, 1,gdal.GDT_Float32)
        dst_ds.SetProjection(im_proj)
        dst_ds.SetGeoTransform(im_geotrans)
        dst_ds.GetRasterBand(1).WriteArray(pic)
        dst_ds.FlushCache()
        print("输出tiff成功")
        # for j in range(1439,-1,-1):#横向翻转
        #     test[:,1439-j]  = pic[:,j]

if __name__ == '__main__':
    opendat('D:/work/shamo/data/data_0810/tmp.20200804.dat',1440,721,56)
        # driver = gdal.GetDriverByName('GTiff')
        # dst_ds = driver.Create('D:/work/shamo/haiyang/3333.tif', 721, 360, 1, gdal.GDT_CFloat32)
        # dst_ds.GetRasterBand(1).WriteArray(d3)
        # dst_ds.FlushCache()
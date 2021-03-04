#_*_ coding:utf-8-*-
import sys
import os
import re
import json
import pandas as pd
import csv
import struct
import pickle
import numpy as np
import collections
import gdal

def save_file(path, item):
        
        # 先将字典对象转化为可写入文本的字符串
        item = json.dumps(item)

        try:
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write(item + ",\n")
                    print("^_^ write success")
            else:
                with open(path, "a") as f:
                    f.write(item + ",\n")
                    print("^_^ write success")
        except Exception as e:
            print("write error==>", e)
def opendat(filename,nx,ny,nz):

    data = np.fromfile(filename,'b')#文件导入
    # 风力级别
    # classw=dict('7':'200 mb','9':'300 mb','13':'500 mb','17':'700 mb','20':'850 mb','25':'1000 mb')
    # aaa=np.zeros((nx,ny,nz)) 
    # U=dict({'UGRD1':'10 mb','UGRD2':'20 mb','UGRD3':'30 mb', 'UGRD4':'50 mb',
    #       'UGRD5':'70 mb','UGRD6':'100 mb','UGRD7':'150 mb','UGRD8':'200 mb','UGRD9':'250 mb','UGRD10':'300 mb',
    #       'UGRD11':'350 mb','UGRD12':'400 mb','UGRD13':'450 mb','UGRD14':'500 mb','UGRD15':'550 mb','UGRD16':'600 mb',
    #       'UGRD17':'650 mb','UGRD18':'700 mb', 'UGRD19':'750 mb','UGRD20':'800 mb','UGRD21':'850 mb','UGRD22':'900 mb',
    #       'UGRD23':'925 mb','UGRD24':'950 mb','UGRD25':'975 mb','UGRD26':'1000 mb'})
    # V=dict({'VGRD1':'10 mb','VGRD2':'20 mb','VGRD3':'30 mb', 'VGRD4':'50 mb','VGRD5':'70 mb','VGRD6':'100 mb',
    #       'VGRD7':'150 mb','VGRD8':'200 mb','VGRD9':'250 mb','VGRD10':'300 mb','VGRD11':'350 mb', 'VGRD12':'400 mb',
    #       'VGRD13':'450 mb','VGRD14':'500 mb','VGRD15':'550 mb','VGRD16':'600 mb','VGRD17':'650 mb','VGRD18':'700 mb',
    #       'VGRD19':'750 mb','VGRD20':'800 mb','VGRD21':'850 mb','VGRD22':'900 mb','VGRD23':'925 mb','VGRD24':'950 mb',
    #       'VGRD25':'975 mb','VGRD26':'1000 mb'})
    U=dict()
    V=dict()
    for t in range(nz):
        
        if t != 9:
            continue

        pic = np.zeros((nx,ny))

        # for i in range(nx):
        #     for j in range(ny):
        #         data = fp.read(4)
        #         elem = struct.unpack("f", data)[0]
        #         pic[i,j]=elem
        n = 721*360
        tmp =  data[t* 721*360*4  : (t + 1) * 721*360*4]
        d2 = struct.unpack(str(n)+"f", tmp)
        d3 = np.reshape(d2,(360,721))
        
        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create('D:/work/shamo/haiyang/3333.tif', 721, 360, 1, gdal.GDT_CFloat32)
        dst_ds.GetRasterBand(1).WriteArray(d3)
        dst_ds.FlushCache()
        
        
        
        
        if t < 26 :
           Key='UGRD'+str(t+1)
        #    print(Key)
           U[Key] = pic.tolist()
        else:
            Key ='VGRD'+format(str(t-26))
            # print(Key)
            V[Key] = pic.tolist()
    # fp.close()
    wind=dict({'U':U,'V':V})
    # sj = json.dumps( wind)

    OUTpath='D:/work/shamo/wind1.json'
    save_file(OUTpath,wind)

if __name__ == '__main__':
    # 读取信息
    opendat('D:/work/shamo/20200721000000.dat',360,721,52)
   
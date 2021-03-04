#_*_ coding:utf-8-*-
import sys
import os
import json
import gdal
import pandas as pd
import numpy as np
from compiler.ast import flatten
from collections import OrderedDict 
#给DAT文件写头文件
def write_hdr(filedir,dirpath,x,y,z):

    if os.path.exists(filedir+'.hdr') :
        pass
    else:      
        h1='ENVI'
        h2='description ='
        h3='File Imported into ENVI. }'
        h4='samples = '+str(x)#列
        h5='lines   = '+str(y)#行
        h6='bands   =  '+str(z)#波段数
        h7='header offset = 0'
        h8='file type = ENVI Standard'
        h9='data type = 4'#数据格式
        h10='interleave = bsq'#存储格式
        h11='sensor type = Unknown'
        h12='byte order = 0'
        h13='x start = 0'
        h14='y start = 0'
        h15='wavelength units = Unknown'
        h=[h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13,h14,h15]
        doc = open(dirpath+filedir+'.hdr', 'w')
        for i in range (len(h)):
           doc.write(h[i] + "\n")
        # print(h[i], end='', file=doc)
        # print('\n', end='', file=doc)
        doc.close()
    return  
# 将数据存储为JSON格式
def save_file(outpath, item):
        
        # 先将字典对象转化为可写入文本的字符串
        item = json.dumps(item)
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
def opendat(input,nx,ny,nz):
    ####获取当前路径下的所有dat文件列表
    #filelist = os.listdir(input)
    # path = os.path.dirname(input)
    for dirpath, dirnames, filenames in os.walk(input):
        print(dirpath,dirnames)
        for filename in filenames:
            print(filename)
            if os.path.splitext(filename)[1] == '.dat':
                filedir = os.path.splitext(filename)[0]#获取文件名。后续更改
                print(filedir)
                basename = os.path.basename(filedir)
    #判断是否有头文件，如果没有，进行生成
                hdr = write_hdr(filedir,dirpath,nx,ny,nz)
   # fp = open(filename,'rb')#文件导入   data1 = list()
                data2 = list()
    #####头文件fp
                header1 = {'lo2': 360, 'nx': nx, 'lo1': 0, 'dx': 0.25, 'ny': ny, 'productTypeName':dirpath+filename, 'dy': 0.25, 'parameterNumberName': 'wind direction', 'la1': 90, 'la2': -90}
                header2 = {'lo2': 360, 'nx': nx, 'lo1': 0, 'dx': 0.25, 'ny': ny, 'productTypeName':dirpath+filename, 'dy': 0.25, 'parameterNumberName': 'wind speed', 'la1': 90, 'la2': -90}
    # 风力级别
                force = dict({'7':'200mb','9':'300mb','13':'500mb','17':'700mb','20':'850mb','25':'1000mb'})
    ####开始解析
                ds = gdal.Open(dirpath+filename)
                # 获取常规信息
                # rows = ds.RasterXSize   #列
                # cols = ds.RasterYSize  #行
                # im_geotrans = ds.GetGeoTransform()#获取仿射矩阵信息
                # im_proj = ds.GetProjection()#获取投影信息
                for kv in force.keys():
                    t = int(kv)

                    OUTpath = dirpath+'/'+'NWP'+'_'+basename+'_'+'UV'+'_'+force[kv]+'.json'#文件输出路径
        #####检测是否已经有json文件存在，如果有，删除，并重做
                    if os.path.exists(OUTpath):
                        os.remove(OUTpath)
                    else:
                        pass
                    print(t)
        #####根据风力级别提取所需的层级数据
                    temp1 = ds.GetRasterBand((t)).ReadAsArray()# U分量值
                    temp2 = ds.GetRasterBand((t+26)).ReadAsArray()# V分量值
                    # 数据测试tiff格式
                    row = temp1.shape[0]  # 行数
                    columns = temp1.shape[1]  # 列数
                    dim = 2  # 通道数
                    # 创建驱动
                    driver = gdal.GetDriverByName('GTiff')
                    # 创建文件
                    dst_ds = driver.Create('D:/work/shamo/haiyang/2.tif', columns, row, dim, gdal.GDT_CFloat32)
                    # 设置几何信息
                    ####dst_ds.SetGeoTransform(im_proj)
                    
                    # # 将数组写入
                    dst_ds.GetRasterBand(1).WriteArray(temp1)
                    dst_ds.GetRasterBand(2).WriteArray(temp2)
                    dst_ds.FlushCache()
        # temp = (temp1.flatten()).tolist()
        ####将二维数组转为一维数组并转为list，存入字典中
                    data1 = (temp1.flatten()).tolist()
                    data2 = (temp2.flatten()).tolist()
                    U = OrderedDict()
                    V = OrderedDict()
                    U['header'] = header1
                    U['data'] = data1
                    V['header'] = header2
                    V['data'] = data2
     #  item = json.dumps(U,sort_keys=True,skipkeys=True)
                    wind = [U,V]
                    save_file(OUTpath,wind)
        # save_file(OUTpath,V)

if __name__ == '__main__':
  ####给定文件路径，以及数据分层所需数据，列，行，波段/层数
    opendat('D:/work/shamo/haiyang/',1440,721,54)
  ####注意修改路径
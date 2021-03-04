#-*- coding: UTF-8 
import sys
import os
import osr
import json
import codecs
from osgeo import gdal, gdal_array 
import cv2
import matplotlib.pyplot as plt
# from osgeo.gdalconst import * 
import numpy as np 
from osgeo import ogr 

def buffer(value,axes):
    ####将数组转成list
    temp = axes
    t = []
    for i in range(len(axes)):
        tt = temp[i].tolist()
        t.append(tt)
    # temp = axes.tolist()
    ct = {"type":"Feature",
            "properties":{'Counter':value},
            "geometry":{
                "type":"MultiLineString",
                "coordinates":t
                }
    }
    
    return ct
###读取tif图像数据返回数组values
def read_tiff(infile,outpath):
    dataset = gdal.Open(infile)
    filename = os.path.basename(infile).split('.')[0]
    if dataset is None:
         print('Unable to open *.tif')
         sys.exit(1)  # 退出
    # projection = dataset.GetProjection()  # 投影
    # transform = dataset.GetGeoTransform()  # 几何信息
    data = dataset.GetRasterBand((1)).ReadAsArray()
    print("数据读取成功")
    ####创建坐标数组
    # lat = np.zeros((data.shape[0],data.shape[1]))
    # for i in range(data.shape[1]):
    #     lat[:,i] = np.array([0+(360/(data.shape[1]-1))*i]*data.shape[0])
    # lon = np.zeros((data.shape[0],data.shape[1]))
    # for j in range(data.shape[0]):
    #     lon[j,:] = np.array([90+(-180/data.shape[1])*j]*data.shape[1])
    ###中值滤波
    # blured = cv2.medianBlur(data,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    # blured = cv2.medianBlur(blured,3)
    #####高斯滤波
    blured = cv2.GaussianBlur(data,(3,3),5)
    blured = cv2.GaussianBlur(blured,(3,3),5)
    blured = cv2.GaussianBlur(blured,(3,3),5)
    blured = cv2.GaussianBlur(data,(3,3),5)
    blured = cv2.GaussianBlur(blured,(3,3),5)
    blured = cv2.GaussianBlur(blured,(3,3),5)    
    data = blured
    ny, nx = np.array(data).shape
    # dt = data.reshape(1,nx*ny)
    lon = np.linspace(0, 360, nx)
    lat = np.linspace(90,-90, ny)
    lon, lat = np.meshgrid(lon, lat)
    layers = int(data.max()-data.min())/2  #等间距为2
    plt.contourf(lon,lat,data,layers,alpha=1,cmap = plt.cm.hot)
    #为等高线填充颜色 10表示按照高度分成10层 alpha表示透明度 cmap表示渐变标准
    C = plt.contour(lon,lat,data,layers,colors='black')
    values = C.layers
    axes = C.allsegs
    ddict = []
    for layer in range(layers):
        buf = buffer(values[layer],axes[layer])
        ddict.append(dict(buf))
    
    geojson = codecs.open(outpath + filename + "-buguolv66.json","w", encoding='utf-8')
    geojson.write(json.dumps({"type":"FeatureCollection", "features":ddict}) + '\n')
    geojson.close()
    # plt.show()
    print('success^_^')

if __name__ == '__main__':
    read_tiff('D:/work/shamo/Contour_result/image/20200804_tmp.tif','D:/work/shamo//Contour_result/geojson/')
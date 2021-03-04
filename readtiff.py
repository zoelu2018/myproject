#-*- coding: UTF-8 
import gdal
import os

dataset = gdal.Open(r"C:/Users/30494/Desktop/LUCD/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7.tif")
im_width = dataset.RasterXSize #栅格矩阵的列数
im_height = dataset.RasterYSize #栅格矩阵的行数
im_bands = dataset.RasterCount #波段数
im_data = dataset.ReadAsArray(0,0,im_width,im_height)#获取数据
im_geotrans = dataset.GetGeoTransform()# 获取投影信息
print(data)
#-*- coding:utf-8 -*- 
import gdal
import sys
import os
import osr
def tiff(data):
    im_geotrans= [60,0.15,0,70,0,-0.15] #左上角坐标，以及分辨率
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS('WGS84')
    im_proj = srs.ExportToWkt()
    row = data.shape[0]  # 行数
    columns =data.shape[1]
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create('D:/work/FY4/fy4AMV/test/test.tif', columns, row, 1,gdal.GDT_Float32)
    dst_ds.SetProjection(im_proj)
    dst_ds.SetGeoTransform(im_geotrans)
    dst_ds.GetRasterBand(1).WriteArray(pic)
    dst_ds.FlushCache()
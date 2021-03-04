#-*- coding: UTF-8 
import sys
import os
import osr
import shapefile
import json
import codecs
from tqdm import tqdm
from osgeo import gdal, gdal_array 
# from scipy.interpolate import spline
import bezier
import matplotlib.pyplot as plt
from osgeo.gdalconst import * 
import numpy as np 
from osgeo import ogr 
from scipy import interpolate
import matplotlib.pyplot as p
import pylab as pl
from scipy.interpolate import griddata
def Shp2JSON(filename,shp_encoding='utf-8',json_encoding='utf-8'):
    reader = shapefile.Reader(filename,encoding=shp_encoding)
     
    # reader = shapefile.Reader(filename,encoding=shp_encoding)
    
    '''提取所有field部分内容'''
    fields = reader.fields[1:]
    
    '''提取所有field的名称'''
    field_names = [field[0] for field in fields]
    # for field in fields:
    #     print(field)
    
    '''初始化要素列表'''
    buffer = []
 
    for sr in tqdm(reader.shapeRecords()):
        record = sr.record
        # 属性转换为列表
        record = [r.decode('gb2312','ignore') if isinstance(r, bytes) else r for r in record]
        # 对齐属性与对应数值的键值对
        atr = dict(zip(field_names, record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom,properties=atr))
        ####摘出数据
        a_array = np.array(buffer[0]['geometry']['coordinates'])
        ###贝塞尔插值
        # curve = bezier.Curve(a_array, degree=1)
        # curve.implicitize()
        
        print(curve.implicitize())
        x = a_array[:,0]
        y = a_array[:,1]
        pl.plot(x,y,'^',color = 'red')
        pl.plot(x,y,color = 'yellow')
        p.legend()
        pl.show()
        #拉格朗日
        xnew = np.linspace(x.min(),x.max(),100)
        # func = interpolate.interp1d(x,y,kind='cubic')
        # ynew = func(xnew)
        # plt.plot(xnew,ynew)
        power_smooth = spline(x,y,xnew)#平滑
        plt.plot(xnew,power_smooth)
        plt.show()
        
        geojson = codecs.open(filename + "-geo.json","w", encoding=json_encoding)
        geojson.write(json.dumps({"type":"FeatureCollection", "features":buffer}) + '\n')
        geojson.close()
        # print('转换成功！')
    print('转换成功')

def getContour(infile,outpath):
    #Read in SRTM data 
    indataset1 = gdal.Open(infile, GA_ReadOnly) #读取数据
    in1 = indataset1.GetRasterBand(1) #获取波段
    basename = os.path.basename(infile).split('.')[0]#获得文件名
    outfile = os.path.join(outpath, '{0}GDAL_TEST2d.shp'.format(basename))#输出文件名
    #Generate layer to save Contourlines in 
    ogr_ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(outfile) #输出格式为shp格式
    ###定义坐标系
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS('WGS84')
    contour_shp = ogr_ds.CreateLayer('contour',srs,ogr.wkbLineString) #创建等值线图层
    
    #等值线的属性列表
    field_defn = ogr.FieldDefn("ID", ogr.OFTInteger) 
    contour_shp.CreateField(field_defn) 
    field_defn = ogr.FieldDefn("contour", ogr.OFTReal) 
    contour_shp.CreateField(field_defn) 
    
    #创建等值线
    gdal.ContourGenerate(in1,2, 0, [], 0, 0, contour_shp, 0, 1) 

    ogr_ds.Destroy() 
    print("等高线生成成功")
    Shp2JSON(filename=outfile,
            shp_encoding='gbk',
            json_encoding='utf-8')
if __name__ == '__main__':
    getContour('D:/work/20200804_tmp_0.25d.tif','D:/work/Contour/SHP/')
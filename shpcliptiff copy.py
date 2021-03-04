# -*- coding:utf-8 -*-
# @Time : 2021/2/2 9:32
# @Author: luxl
# @python-v: 3.9
# @File : shpcliptiff.py.py

from geopandas import *
import rasterio as rio
import rasterio.mask
import os
import pymongo

def connDB():
    client = pymongo.MongoClient('121.36.13.81', 27071)
    # 连接数据库,账号密码认证
    # 连接系统默认数据库admin
    db = client.admin
    db.authenticate('shk401', 'shkshkshk')

    return client

def getdata(shpdatafile,rasterfile,collection):

    rastertime = os.path.basename(rasterfile).split('_')[6][:8]
    rasterprod = os.path.basename(rasterfile).split('_')[4]
    rastertype = os.path.basename(rasterfile).split('_')[11].split('.')[0]
    

    shpdata = geopandas.GeoDataFrame.from_file(shpdatafile)
    rasterdata = rio.open(rasterfile)
    # shpdata = shpdata.to_crs(rasterdata.crs)
    type_data = []
    id_code = []
    for key in range(0,len(shpdata)):
        geo = shpdata.geometry[key]
        feature = [geo.__geo_interface__]
        try:
            out_image, out_transform = rio.mask.mask(rasterdata, feature, all_touched=True, crop=True, nodata=rasterdata.nodata)
        except Exception as e:
            continue
        objectid = int(shpdata.OBJECTID[key])
        # out_meta = rasterdata.meta.copy()
        # out_meta.update({"driver": "GTiff",
        #                  "height": out_image.shape[1],
        #                  "width": out_image.shape[2],
        #                  "transform": out_transform})
        # band_mask = rasterio.open('C:/Users/30494/Desktop/testtif/test.tif', "w", **out_meta)
        # band_mask.write(out_image)
        #剔除无效值
        # out_list = out_image.data.tolist()
        # out_list = out_list[0]
        # out_data = []
        # for k in range(len(out_list)):
        #     for j in range(len(out_list[k])):
        #         if out_list[k][j] >= 0:
        #             out_data.append(out_list[k][j])
        
        out_data = out_image.max()
        dta = {
            "date":rastertime,
            "value": int(out_data)
        }
        if rasterprod == 'CYE':
                
            info = {
                "yield":{
                    type: dta
                }

            }

        elif rasterprod == 'CGM':
            info = {
                "growth":{
                    rastertype: dta
                }

            }

        oldrecord = collection.find_one({"fcode":str(objectid)})

        collection.update_one(
                        {"fcode": '56826'},
                        {'$set':{
                            "yield":{
                            rastertype: dta},
                            "crop":type}}
        )




    #     # type_data.append(dta)
    #     # id_code.append(objectid)
    # return type_data,id_code

def update_dta():
    client = connDB()
    shgfview = client.shgfview
    collection = shgfview.landuseinfos
    return collection





if __name__ == '__main__':
    inputdir = "C:/Users/30494/Desktop/testtif/test" #
    shpdatafile = 'C:/Users/30494/Desktop/testtif/shp_jan/cmdk_jan.shp'
    for root, dirs, files in os.walk(inputdir):
        for file in files:
            if os.path.splitext(file)[1] == '.tif':
                rasterfile = os.path.join(inputdir, file)
                collection =update_dta()
                type_data, id_code =  getdata(shpdatafile, rasterfile,collection)
               









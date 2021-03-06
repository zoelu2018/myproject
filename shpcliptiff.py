# -*- coding:utf-8 -*-
# @Time : 2021/2/2 9:32
# @Author: luxl
# @python-v: 3.9
# @File : shpcliptiff.py.py

import geopandas
import rasterio as rio
import rasterio.mask
import os
import pymongo

CGM_single = {'0':'NODATA','1':'长势较差','2':'长势正常','3':'长势较好','4':'长势优良'}
SMM_single = {'0':'NODATA','1':'一类墒情','2':'二类墒情','3':'三类墒情','4':'三类墒情'}

def connDB():
    client = pymongo.MongoClient('10.1.100.40', 27071)
    # client = pymongo.MongoClient('121.36.13.81', 27071)
    # 连接数据库,账号密码认证
    # 连接系统默认数据库admin
    db = client.admin
    db.authenticate('shinetekview', 'yCH4EaYeNoJR','shinetekview')
    # db.authenticate('shk401', 'shkshkshk')

    return client
def update_dta():
    client = connDB()
    shinetekview = client.shinetekview
    collection = shinetekview.landuseinfos
    return collection

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
        oldrecord = collection.find_one({"fcode":str(objectid)}) 
        out_data = out_image.max()
        
    
        if rasterprod == 'CYE':

            dta = [{"date":rastertime,"value": int(out_data)}]

            try:
                oldrecord['yield'][rastertype].append(dta)
                dta = oldrecord['yield'][rastertype]
            except Exception as e:
                dta = dta
            oldrecord['yield'][rastertype].append(dta)    
            collection.update_one(
                            {"fcode": str(objectid)},
                            {'$set':{
                                "yield":{
                                rastertype:oldrecord['yield'][rastertype] },
                                 "cropInfo":{rastertype:[rastertime]}}}
            )

            print("属性更新 %s 完毕" % objectid)

        elif rasterprod == 'CGM':

            # 获取长势和墒情数据
            CGM_ = CGM_single[str(out_data)]
            CGM_dta = [{"date":rastertime,"value": CGM_ }]

            SMM_ = SMM_single[str(out_data)]
            SMM_dta = {"date":rastertime,"value": SMM_ }

            Crop_dta = {rastertype:rastertime}

            # 更新长势数据
            try:
                oldrecord['growth'][rastertype].append(CGM_dta)
                CGM_dta = oldrecord['growth'][rastertype]
            except Exception as e:
                CGM_dta = CGM_dta
            try:
                oldrecord['SMM'].append(SMM_dta)
                SMM_dta = oldrecord['SMM']

                oldrecord['cropInfo'].append(Crop_dta)
                proTime = oldrecord['cropInfo']
            
            except Exception as e:
                SMM_dta = [SMM_dta]
                proTime = [Crop_dta]
            try:
                oldrecord['growth'].update({rastertype:CGM_dta})
                CGM_DIC = oldrecord['growth']
            except Exception as e:
                CGM_DIC = CGM_dta



            


                
            collection.update_one(
                            {"fcode": str(objectid)},
                            {'$set':{
                                "growth":CGM_DIC,
                                "cropInfo":proTime,
                                "SMM":SMM_dta
                            }
                            }
            )
            print("属性更新 %s 完毕" % objectid)








if __name__ == '__main__':
    inputfile = "C:/Users/30494/Desktop/testtif/test/SENTINEL2A_MSI_Latlon_L3_CGM_NULL_20201030000000_20201030000000_10M_POAI_D_Rice.tif" #
    shpdatafile = 'C:/Users/30494/Desktop/testtif/shp_jan/cmdk_jan.shp'
    collection =update_dta()
    getdata(shpdatafile, inputfile,collection)
    









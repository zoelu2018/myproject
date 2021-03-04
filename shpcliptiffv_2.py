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

CGM_single = {'0':'','1':'长势较差','2':'长势正常','3':'长势较好','4':'长势优良'}
SMM_single = {'0':'','1':'一类墒情','2':'二类墒情','3':'三类墒情','4':'三类墒情'}
CROP_single = {'Rice':'水稻','Rape':'油菜'}
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
        if (out_data != 0):
    
            if rasterprod == 'CYE':

            # 获取长势和墒情数据
                CYE_ = float(out_data)
                crop_ = CROP_single[rastertype]
                temp = {"name":crop_,"value": CYE_,"enName":rastertype}
                CYE_dta = {"date":rastertime,"stats":[temp]}
                Crop_dta = {"date":rastertime,"name":crop_,"enName":rastertype}
            

                # 更新估产数据
                try:
                    oldrecord['growth'].append(CGM_dta)
                    CGM_dta = oldrecord['growth']
                    
                
                except Exception as e:
                    CYE_dta = [CYE_dta]  
                    

                try:
                    oldrecord['cropInfo'].append(Crop_dta)
                    proTime = oldrecord['cropInfo']
                except Exception as e:
                    proTime = [Crop_dta] 


                collection.update_one(
                                {"fcode": str(objectid)},
                                {'$set':{
                                    "yield":CYE_dta,
                                    "cropInfo":proTime
                                }
                                }
                )
                print("属性更新 %s 完毕" % objectid)


            elif rasterprod == 'CGM':

                # 获取长势和墒情数据
                CGM_ = CGM_single[str(out_data)]
                crop_ = CROP_single[rastertype]
                SMM_ = SMM_single[str(out_data)]

                test =  {"name":crop_,"CGM": CGM_,"value":float(out_data),"enName":rastertype,"SMM":SMM_}

                CGM_dta = {"date":rastertime,"stats":[test]}
                SMM_dta = {"date":rastertime,"stats":[{"value": SMM_}]}
                Crop_dta = {"date":rastertime,"name":crop_,"enName":rastertype}

                # 更新长势数据
                try:
                    oldrecord['growth'].append(CGM_dta)
                    CGM_dta = oldrecord['growth']
                    oldrecord['SMM'].append(SMM_dta)
                    SMM_dta = oldrecord['SMM']
                    oldrecord['cropInfo'].append(Crop_dta)
                    proTime = oldrecord['cropInfo']
                
                except Exception as e:
                    CGM_dta = [CGM_dta]
                    SMM_dta = [SMM_dta]
                    proTime = [Crop_dta]    
                collection.update_one(
                                {"fcode": str(objectid)},
                                {'$set':{
                                    "growth":CGM_dta,
                                    "cropInfo":proTime,
                                    "SMM":SMM_dta
                                }
                                }
                )
                print("属性更新 %s 完毕" % objectid)








if __name__ == '__main__':
    # inputfile = "C:/Users/30494/Desktop/testtif/test/SENTINEL2A_MSI_Latlon_L3_CYE_NULL_20200605000000_20200805000000_10M_POAX_D_Rice.tif" #
   
   
    inputdir = "C:/Users/30494/Desktop/testtif/test" #
    shpdatafile = 'C:/Users/30494/Desktop/testtif/shp_jan/cmdk_jan.shp'
    timelist = {}
    for root, dirs, files in os.walk(inputdir):
        for file in files:
            if os.path.splitext(file)[1] == '.tif':
                time = os.path.basename(file).split('_')[6]
                # time.append(time)
                timelist.update({file:time})              
    datalist = sorted(timelist.items(), key = lambda kv:(kv[1], kv[0]))
    for key in range(len(datalist)-1,-1,-1):
        # print(key,timelist[key])
        file_ = datalist[key][0]
        rasterfile = os.path.join(inputdir, file_)
        print(rasterfile)
        collection =update_dta()
        getdata(shpdatafile, rasterfile,collection)
        print(rasterfile+'success')


    # for time_ in timelist:
    #     for root, dirs, files in os.walk(inputdir):
    #         for file in files:
    #             if (os.path.splitext(file)[1] == '.tif') & (time_ in file):
                # rasterfile = os.path.join(inputdir, file)
                # collection =update_dta()
                # getdata(shpdatafile, rasterfile,collection)
                # print(rasterfile+'success')

               
    









#!/usr/bin/env python
# coding:utf-8

import json
import pymongo


def resolveJson(inputfile):
    file = open(inputfile, "rb")
    fileJson = json.load(file)
    features = fileJson["features"]
    optDB(features)


def palettes(fielduse):
    palettes = {'liangtian': [int("255"), int("204"), int("33"), int("1")],
                'caitian': [int("180"), int("195"), int("34"), int("1")],
                'shuichan': [int("54"), int("196"), int("208"), int("1")],
                'lindi': [int("125"), int("147"), int("75"), int("1")],
                'guoyuan': [int("81"), int("87"), int("129"), int("1")],
                'miaomu': [int("211"), int("223"), int("123"), int("1")],
                'qita': [int("132"), int("141"), int("143"), int("1")],
                'weiding': [int("188"), int("137"), int("108"), int("1")],
                'jingzuo': [int("188"), int("137"), int("108"), int("1")],
                'chuqin': [int("145"), int("102"), int("41"), int("1")],
                'huahui': [int("255"), int("100"), int("207"), int("1")],
                'xxny': [int("241"), int("85"), int("37"), int("1")],
                'ssyd': [int("201"), int("178"), int("205"), int("1")],
                'kjyjytj': [int("62"), int("93"), int("191"), int("1")]
    }
    return palettes[fielduse]


def pinyin(ch):
    chpy = {u'粮田': 'liangtian', u'菜田': 'caitian', u'水产': 'shuichan', u'林地': 'lindi', u'果园': 'guoyuan', u'苗木': 'miaomu',
    u'其它': 'qita', u'未确定用途': 'weiding', u'经作': 'jingzuo', u'畜禽': 'chuqin', u'花卉':'huahui', u'休闲农业': 'xxny',
    u'设施用地': 'ssyd', u'科研研究与推广': 'kyyjytg'}
    return chpy[ch]


def connDB():
    client = pymongo.MongoClient('121.36.13.81', 27071)
    # 连接数据库,账号密码认证
    # 连接系统默认数据库admin
    db = client.admin
    db.authenticate('shk401', 'shkshkshk')

    return client


def get_max_lon_lat(geometry):
    length = len(geometry['coordinates'])
    if 'coordinates' in geometry and length > 0:
        coordinates = geometry['coordinates']
        maxlon = minlon = 0
        maxlat = minlat = 0
        for c in coordinates[0]:
            lon = c[0]
            lat = c[1]
            if maxlon < lon:
                maxlon = lon
            else:
                minlon = lon
            if maxlat < lat:
                maxlat = lat
            else:
                minlat = lat
    return [minlon, maxlat, maxlon, minlat] 


def optDB(features):
    # 连接上海高分数据库
    client = connDB()
    shgfview = client.shgfview
    collection = shgfview.agrilands
    collection1 = shgfview.landuseinfos
    # 田块属性
    agrilands_attrs = []
    landuseinfos_attrs = []

    # 土地使用
    usage = [{'usage': 'liangtian', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'caitian', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'shuichan', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'lindi', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'guoyuan', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'miaomu', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'qita', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'weiding', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'jingzuo', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'chuqin', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'huahui', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'xxny', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'ssyd', 'fieldnum': int(0), 'landarea': float(0.00)},
             {'usage': 'kyyjytg', 'fieldnum': int(0), 'landarea': float(0.00)}
        ] 

    for f in features:
        geometry = f["geometry"]
        minlon, maxlat, maxlon, minlat = get_max_lon_lat(geometry)
        properties = f["properties"]
        USAGE = properties["USAGE"]
        ch = USAGE.split(',')[0]
        crop = USAGE.split(',')[1]
        pyin = pinyin(ch)
        totalarea = properties["TOTALAREA"]
        lon = properties[u"经度"]
        lat = properties[u"纬度"]
        # palette = palettes(pyin)
        # for u in usage:
        #     if pyin == u['usage']:
        #         u['fieldnum'] = u['fieldnum']+1
        #         u['landarea'] = u['landarea']+totalarea
        #         u['palette'] = palette
        fieldattrs = {'agricase': '5fd064f940f1f2257e673395', "fcode": str(properties["OBJECTID"]), 'box': [minlon, maxlat, maxlon, minlat], 
        "usage": pyin, "crop": crop, "usearea": properties["USEAREA"], "totalarea": totalarea, "lon": lon, "lat": lat, "geometry": geometry,"province":"上海", "city":"崇明区", "town": "", "village":""}

        fieldattrs1 = {'agricase': '5fd064f940f1f2257e673395', "fcode": str(properties["OBJECTID"]), "landuse": USAGE, "inspectionarea": properties["USEAREA"], "lon": lon, "lat": lat, "growersType":"",
        "growersName":"", "idnum":"","tel":" ","retailnames":[],"createtime":"20210201180317"} 
        agrilands_attrs.append(fieldattrs)
        landuseinfos_attrs.append(fieldattrs1)
    collection.insert_many(agrilands_attrs)
    collection1.insert_many(landuseinfos_attrs)
    client.close()


if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     stderr.write('$error|%s' % json.dumps({'errormsg':'参数错误'}))
    #     stderr.flush()
    #     sys.exit(10)
    inputfile = r"C:\Users\shangzm\Downloads\cmdk_jan.json"
    # 解析
    resolveJson(inputfile)

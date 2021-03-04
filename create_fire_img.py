# _*_coding:utf-8_*_
import numpy as np
import gdal
import osr
import sys
import traceback
import json
from sys import argv, stdout, stderr
from decimal import Decimal
from customerr.cus_error import BandError, RangeError
from datahandler.gtifwriter import GTifWriter
from proj_name import name_proj

FILLVALUE = 0


def create_fire_img(inputFile, outputFile, box, res, projname='latlon'):
    # box记录的是左上右下
    top_lon, top_lat, btm_lon, btm_lat = box
    # 计算图像大小
    max_lon = Decimal(str(box[2]))
    min_lon = Decimal(str(box[0]))
    lon_res = Decimal(str(float(res)))
    max_lat = Decimal(str(box[1]))
    min_lat = Decimal(str(box[3]))
    lat_res = Decimal(str(float(res)))
    img_height = int(round((max_lat - min_lat) / lat_res + Decimal(0.5)))
    img_width = int(round((max_lon - min_lon) / lon_res + Decimal(0.5)))
    # 创建空图像
    data_buf = np.full((img_height, img_width), FILLVALUE, dtype=np.int32)
    # 读取文件
    fireJson = {}
    with open(inputFile, 'r') as jsonFile:
        fireJson = json.load(jsonFile)["result"]
    stdout.write('$process|%d\n' % 40)
    stdout.flush()
    for firePoint in fireJson:
        lat = Decimal(str(firePoint["lat"]))
        lon = Decimal(str(firePoint["lon"]))
        i = int(round(Decimal(str(max_lat - lat)) / lat_res))
        j = int(round(Decimal(str(lon - min_lon)) / lon_res))
        data_buf[i, j] = 1
    stdout.write('$process|%d\n' % 80)
    stdout.flush()
    # 设置投影
    if projname == 'latlon':
        osr = osr.SpatialReference()
        osr.ImportFromEPSG(4326)
    else:
        proj = name_proj(projname)
    # 写出数据
    tif_file = GTifWriter(lon_res, [top_lat, top_lon], data_buf, proj)
    tif_file.write(outputFile)
    stdout.write('$process|%d\n' % 100)
    stdout.flush()
    stdout.write('$output|%s\n' % outputFile)
    stdout.flush()
    return


if __name__ == "__main__":

    INPUTFILE = sys.argv[1]
    OUTPUTFILE = sys.argv[2]
    LEFTLON = sys.argv[3]
    LEFTLAT = sys.argv[4]
    RIGHTLON = sys.argv[5]
    RIGHTLAT = sys.argv[6]
    RES = sys.argv[7]
    PROJSTR = sys.argv[8]
    # INPUTFILE = r"F:\\ZL\\data\\fire\\cs\\MTU5NDgwNTE4ODM4OTQwNzYx.json"
    # OUTPUTFILE = r"F:\\ZL\\data\\fire\\cs\\MTU5NDgwNTE4ODM4OTQwNzYx.tif"
    # LEFTLON = -180
    # LEFTLAT = 90
    # RIGHTLON = 180
    # RIGHTLAT = -90
    # RES = 1
    # PROJSTR = "+lon_0=112 +k=1 +ellps=WGS84 +datum=WGS84 +y_0=0 +errcheck=True +proj=longlat +x_0=0 +units=m +no_defs"

    try:
        create_fire_img(INPUTFILE, OUTPUTFILE, [LEFTLON, LEFTLAT, RIGHTLON, RIGHTLAT], RES, PROJSTR)
    except IOError as io_err:
        stderr.write('$error|%s' % io_err + " at create_fire_img.py!!! " + ':' + traceback.format_exc())
        stderr.flush()
        sys.exit(2)
    except OverflowError as outm_err:
        stderr.write('$error|%s' % outm_err + " at create_fire_img.py!!! " + ':' + traceback.format_exc())
        stderr.flush()
        sys.exit(3)
    except BandError as band_err:
        stderr.write('$error|%s' % band_err + " at create_fire_img.py!!! " + ':' + traceback.format_exc())
        stderr.flush()
        sys.exit(4)
    except RangeError as range_err:
        stderr.write('$error|%s' % range_err + " at create_fire_img.py!!! " + ':' + traceback.format_exc())
        stderr.flush()
        sys.exit(5)
    except Exception as err:
        stderr.write('$error|%s' % err + " at create_fire_img.py!!! " + ':' + traceback.format_exc())
        stderr.flush()
        sys.exit(99)

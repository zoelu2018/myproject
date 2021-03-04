# -*- coding:utf-8 -*-
# @Time : 2020/12/9 10:48
# @Author: luxl
# @python-v: 2.7
# @File : CONVERTTIF2JPG.py.py
import gdal
from PIL import Image
import pandas as pd
import numpy as np
import os
def main(dataset, outputfile):
    # dataset = gdal.Open(r"C:/Users/30494/Desktop/LUCD/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7.tif")
    # outputfile = "C:/Users/30494/Desktop/LUCD/result.jpg"
    im_width = dataset.RasterXSize  # 栅格矩阵的列数
    im_height = dataset.RasterYSize  # 栅格矩阵的行数
    im_bands = dataset.RasterCount  # 波段数
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 获取数据
    df = pd.read_excel("D:/work/projects/TIF2JPG/cb.xlsx")
    imgdata = df["value"].values
    RGBA = df["RGBA"].values
    # rgbimg = Image.new("RGBA", im_data.shape)
    arraypng = np.zeros((3, im_height, im_width), dtype=np.uint8)
    for j in range(len(imgdata)):
        mask = im_data == imgdata[j]
        arraypng[0][mask] = tuple(eval(RGBA[j]))[0]
        arraypng[1][mask] = tuple(eval(RGBA[j]))[1]
        arraypng[2][mask] = tuple(eval(RGBA[j]))[2]
        # arraypng[3][mask] = RGBA[j][3]
    aaa=arraypng.transpose(1, 2, 0)
    # print aaa.shape
    img = Image.fromarray(aaa).convert('RGB')  # 将数组转化回图片
    img.save(outputfile)  # 将数组保存为图片
    print(outputfile, str("转换完成"))
if __name__ == '__main__':
    for dir,_,filelist in os.walk("C:/Users/30494/Desktop/test/tile/all"):
        for file in filelist:
            filetext = os.path.splitext(file)[1]
            if filetext =='.TIF':
                dataset = gdal.Open(os.path.join(dir,file))
                outputfile = os.path.join("C:/Users/30494/Desktop/test/tile/all", os.path.splitext(file)[0]+".jpg")
                main(dataset,outputfile)





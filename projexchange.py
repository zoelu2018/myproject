# -*- coding: utf-8 -*-
import argparse
import os
import sys
import numpy as np
import gdal,osr
import h5py


def UTM2Latlon(inputfile,outfile):

    try:

        ds_d = gdal.Open(inputfile,gdal.GA_ReadOnly)
        GS = gdal.Warp(outfile, ds_d, dstSRS='EPSG:4326')
        del ds_d

        ds = gdal.Open(outfile)
        geotrans = ds.GetGeoTransform()
        ltlat = geotrans[3]
        ltlon = geotrans[0]
        res = geotrans[1]
        list = [1, 2, 4, 8, 16, 32,64,128,256]
        ds.BuildOverviews(overviewlist=list)
        ovrds = gdal.Open(outfile+'.ovr', gdal.GA_Update)
        ovrds.SetGeoTransform([ltlon, res, 0.0, ltlat, 0.0, -res])
        proj = osr.SpatialReference()
        proj.SetWellKnownGeogCS('WGS84')
        ovrds.SetProjection(proj.ExportToWkt())
        del ds
        print("%s 处理结束" % outfile)
    except Exception as e:
        print(e)


def Latlon2(inputfile):

    try:



        ds = gdal.Open(inputfile)
        geotrans = ds.GetGeoTransform()
        ltlat = geotrans[3]
        ltlon = geotrans[0]
        res = geotrans[1]
        list = [1, 2, 4, 8, 16, 32,64,128,256]
        ds.BuildOverviews(overviewlist=list)
        ovrds = gdal.Open(inputfile+'.ovr', gdal.GA_Update)
        ovrds.SetGeoTransform([ltlon, res, 0.0, ltlat, 0.0, -res])
        proj = osr.SpatialReference()
        proj.SetWellKnownGeogCS('WGS84')
        ovrds.SetProjection(proj.ExportToWkt())
        del ds
        print("%s 处理结束" % inputfile)
    except Exception as e:
        print(e)

def Latlon(inputfile):

    try:
        ds = gdal.Open(inputfile)
        list = [1, 2, 4, 8, 16, 32,64,128,256]
        ds.BuildOverviews(overviewlist=list)
        ovrds = gdal.Open(inputfile+'.ovr', gdal.GA_Update)
        ovrds.SetGeoTransform([119, 0.00720720720720728, 0.0, 38, 0.0, -0.0070175438596491])
        proj = osr.SpatialReference()
        proj.SetWellKnownGeogCS('WGS84')
        ovrds.SetProjection(proj.ExportToWkt())
        del ds
        print("%s 处理结束" % inputfile)
    except Exception as e:
        print(e)


def pngLatlon(inputfile):

    try:
        ds = gdal.Open(inputfile)
        list = [1, 2, 4, 8, 16, 32,64,128,256]
        ds.BuildOverviews(overviewlist=list)
        ovrds = gdal.Open(inputfile+'.ovr', gdal.GA_Update)
        ovrds.SetGeoTransform([115.383094788, 0.000208325, 0.0, 29.8460979462, 0.0, -0.000208325])
        proj = osr.SpatialReference()
        proj.SetWellKnownGeogCS('WGS84')
        ovrds.SetProjection(proj.ExportToWkt())
        del ds
        print("%s 处理结束" % inputfile)
    except Exception as e:
        print(e)

def HDF2OVR(inputfile):

    try:
        
        ds = gdal.Open(inputfile)
        list = [1, 2, 4, 8, 16, 32,64,128,256]
        ds.BuildOverviews(overviewlist=list)
        ovrds = gdal.Open(inputfile+'.ovr', gdal.GA_Update)
        ovrds.SetGeoTransform([115.383094788, 0.000208325, 0.0, 29.8460979462, 0.0, -0.000208325])
        proj = osr.SpatialReference()
        proj.SetWellKnownGeogCS('WGS84')
        ovrds.SetProjection(proj.ExportToWkt())
        del ds
        print("%s 处理结束" % inputfile)
    except Exception as e:
        print(e)

if __name__ =='__main__':
    # filedir = 'C:/Users/30494/Desktop/testtif/SOURCE/'
    # for root,dirs,files in os.walk(filedir):
    #     for file in files:
    #         if os.path.splitext(file)[1] =='.tif':
    #             infile = os.path.join(filedir,file)
    #             bsname =  os.path.basename(file)
    #             newname = bsname.replace("UTM","LatLon")
    #             outfile = os.path.join(filedir,newname)
    #             UTM2Latlon(infile,outfile)

    file= 'C:/Users/30494/Desktop/testtif/SENTINEL1A_IW_Latlon_L3_WATER_NULL_20200626000000_20200626235959_20M_POAD_X.png'
    pngLatlon(file)
    # bsname =  os.path.basename(file)
    # newname = bsname.replace("UTM","LatLon")
    # filedir = 'D:/WeChat/WeChat Files/wxlin-304948344/FileStorage/File/2021-02/'
    # outfile = os.path.join(filedir,newname)
    # UTM2Latlon(file,outfile)







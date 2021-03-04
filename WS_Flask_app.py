# -*- coding: utf-8 -*- 
import base64
from gevent.pywsgi import WSGIServer
from flask_cors import CORS
from flask import Flask,request,Response,send_from_directory
from flask_restful import Resource, Api, url_for
import sys
import json
import os
import time
import numpy as np
reload(sys)
sys.setdefaultencoding('utf-8')

from WSconfig import outputpath,IDLbatTEC,IDLbatF107,IDLbatfoF2,IDLbatRDst,IDLbatFDst
from JsMapPicture import JspictureDraw
from JpMapPicture import TEC_jpPicture
from JrMapPicture import TEC_jrPicture

from foF2_Js import foF2_jsPicture
from F107_Js import F107_jsPicture
from Dst_Js import Dst_jsPicture

from kLineData import KLineDataCalculate,KLineDataCalculate1
from PDFpicture import PowerPDFpicture

# 解决json格式的问题
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, time):
            return obj.__str__()
        else:
            return super(NpEncoder, self).default(obj)


#接收整型数字参数
app=Flask(__name__)

api = Api(app)

class PNGINFO(Resource):

    def get(self):

        methodName = request.args['method']
        product = request.args['product']
        filepath = request.args['dirpath']
        startTime = request.args['startTime']
        endTime = request.args['endTime']
        timess = request.args['timess']
        win_envss = request.args['win_envss']
        mode = request.args['mode']


        if methodName == "GPS_TEC" :

            startDaytime = startTime + "_" + endTime

            startDaytime12 = startTime + "_" + startTime[:8] + "2359"

            filepath1 = os.path.dirname(filepath) + "/"

            hdffile = outputpath + 'WTEC_NASA_GLL_' + startDaytime12 + '_2.5Lat_5.0Lon_2Hour_Js_Jp_Jr.h5'

            if not os.path.exists(hdffile):

                cmdStr = IDLbatTEC + " " +str(filepath1) + " " + str(startDaytime) + " " + str(outputpath) + " " + str(timess) + " " + str(win_envss)
                os.system(cmdStr)


            if product == "Js" :

                outfilelist = JspictureDraw(startTime,endTime,hdffile,outputpath)

                data = {}
                datalist = []
                data["dataTypeKey"] = 'GPS_TEC'
                data["handelKey"] = product
                dataNameList1=[]
                dataNameList1.append(os.path.basename(filepath))
                data["dataNameList"] = dataNameList1

                for i in range(len(outfilelist)):

                    js11dict = {}

                    pngname = outfilelist[i]

                    pngbasename = os.path.basename(pngname)

                    yeartime = pngbasename[0:4]
                    monthtime = pngbasename[4:6]
                    daytime = pngbasename[6:8]
                    hourtime = pngbasename[8:10]

                    js11dict["name"] = methodName + " " + yeartime + "年" + monthtime + "月" + daytime + "日" + hourtime + "时" + "00分" + "的JS指数计算结果"

                    abs_path = os.path.abspath(outfilelist[i])

                    js11dict['stream_url'] = url_for('PNGStream', DataPath=abs_path)
                    js11dict['download_url'] = url_for('PNGDownLoad', DataPath=abs_path)

                    datalist.append(js11dict)

                data["imgList"] = datalist

                j = json.dumps(data,ensure_ascii=False,cls=MyEncoder)
                return Response(j,mimetype='application/json')

            elif product == "Jr" :

                localtimes = time.time()

                pngfile = outputpath + str(localtimes) + "_"+startDaytime + "_Jr.png"

                TEC_jrPicture(startTime,endTime,hdffile,pngfile)

                data = {}
                datalist = []
                data["dataTypeKey"] = 'GPS_TEC'
                data["handelKey"] = product
                dataNameList1=[]
                dataNameList1.append(os.path.basename(filepath))
                data["dataNameList"] = dataNameList1

                js11dict = {}
                js11dict["name"] = methodName+ " " + startDaytime + "的Jr指数计算结果"

                abs_path = os.path.abspath(pngfile)
                js11dict['stream_url'] = url_for('PNGStream', DataPath=abs_path)
                js11dict['download_url'] = url_for('PNGDownLoad', DataPath=abs_path)
                datalist.append(js11dict)

                data["imgList"] = datalist

                j = json.dumps(data,ensure_ascii=False,cls=MyEncoder)
            
                return Response(j,mimetype='application/json')

            elif product == "Jp" :

                localtimes = time.time()

                pngfile = outputpath + str(localtimes) + "_" + startDaytime + "_Jp.png"
                TEC_jpPicture(startTime,endTime,hdffile,pngfile)

                data = {}
                datalist = []
                data["dataTypeKey"] = 'GPS_TEC'
                data["handelKey"] = product
                dataNameList1=[]
                dataNameList1.append(os.path.basename(filepath))
                data["dataNameList"] = dataNameList1

                js11dict = {}
                js11dict["name"] = methodName+ " " + startDaytime + "的Jp指数计算结果"

                abs_path = os.path.abspath(pngfile)
                js11dict['stream_url'] = url_for('PNGStream', DataPath=abs_path)
                js11dict['download_url'] = url_for('PNGDownLoad', DataPath=abs_path)
                datalist.append(js11dict)

                data["imgList"] = datalist

                j = json.dumps(data,ensure_ascii=False,cls=MyEncoder)
            
                return Response(j,mimetype='application/json')

        elif methodName == "foF2" :

            startDaytime = startTime + "_" + endTime

            hdffile = outputpath + 'foF2_2451_GLL_' + startDaytime + '_1Hour_Js.h5'

            if not os.path.exists(hdffile):

                cmdStr = IDLbatfoF2 + " " +filepath + " " + startDaytime + " " + outputpath + " " + str(timess) + " " + str(win_envss)
                os.system(cmdStr)

            localtimes = time.time()
            pngfile = outputpath + str(localtimes) + "_" + startDaytime + "_foF2_Js.png"
            foF2_jsPicture(hdffile,pngfile)

            DataName = "JS_foF2"
            kLineDatalist,Time123List,JS_Dstlist1 = KLineDataCalculate(startTime,endTime,DataName,hdffile)
            
            data = {}
            datalist = []
            data["dataTypeKey"] = 'foF2'
            data["handelKey"] = product
            dataNameList1=[]
            dataNameList1.append(os.path.basename(filepath))
            data["dataNameList"] = dataNameList1

            js11dict = {}
            js11dict["name"] = methodName+ " " + startDaytime+"的Js指数计算结果"
            abs_path = os.path.abspath(pngfile)
            js11dict['stream_url'] = url_for('PNGStream', DataPath=abs_path)
            js11dict['download_url'] = url_for('PNGDownLoad', DataPath=abs_path)
            datalist.append(js11dict)
            data["imgList"] = datalist

            js12dict = {}
            js12dict["xData"] = Time123List
            js12dict["yData"] = JS_Dstlist1
            js12dict["name"] = methodName+ " " + startDaytime+"的Js指数计算结果"
            data["LineData"] = js12dict

            js13dict = {}
            js13dict["data"] = kLineDatalist
            js13dict["name"] = methodName+ " " + startDaytime+"的Js指数K线图"
            data["kLineData"] = js13dict


            group1list,group2list = PowerPDFpicture(hdffile)
            js14dict = {}
            js14dict["group1"] = group1list
            js14dict["group2"] = group2list
            js14dict["name"] = methodName+ " " + startDaytime+"的功率谱PDF图"
            data["spData"] = js14dict

            j = json.dumps(data,ensure_ascii=False,cls=MyEncoder)
            
            return Response(j,mimetype='application/json')

        elif methodName == "Flux_107" :

            startDaytime = startTime + "_" + endTime

            hdffile = outputpath + 'FLUX_SWPC_GLL_' + startDaytime + '_1DayX_Js.h5'

            if not os.path.exists(hdffile):

                cmdStr = IDLbatF107 + " " +filepath + " " + startDaytime + " " + outputpath + " " + str(timess) + " " + str(win_envss)
                os.system(cmdStr)


            localtimes = time.time()

            pngfile = outputpath + str(localtimes) + "_" + startDaytime + "_F107_Js.png"
            F107_jsPicture(hdffile,pngfile)

            DataName = "JS_F107"
            kLineDatalist,Time123List,JS_Dstlist1 = KLineDataCalculate1(startTime,endTime,DataName,hdffile)
            group1list,group2list = PowerPDFpicture(hdffile)

            data = {}
            datalist = []
            data["dataTypeKey"] = 'F107'
            data["handelKey"] = product

            dataNameList1=[]
            dataNameList1.append(os.path.basename(filepath))
            data["dataNameList"] = dataNameList1

            js11dict = {}
            js11dict["name"] = methodName+ " " + startDaytime+"的Js指数计算结果"

            abs_path = os.path.abspath(pngfile)
            js11dict['stream_url'] = url_for('PNGStream', DataPath=abs_path)
            js11dict['download_url'] = url_for('PNGDownLoad', DataPath=abs_path)
            datalist.append(js11dict)
            data["imgList"] = datalist

            js12dict = {}
            js12dict["xData"] = Time123List
            js12dict["yData"] = JS_Dstlist1
            js12dict["name"] = methodName+ " " + startDaytime+"的Js指数折线图"
            data["LineData"] = js12dict

            js13dict = {}
            js13dict["data"] = kLineDatalist
            js13dict["name"] = methodName+ " " + startDaytime+"的Js指数K线图"
            data["kLineData"] = js13dict

            js14dict = {}
            js14dict["group1"] = group1list
            js14dict["group2"] = group2list
            js14dict["name"] = methodName+ " " + startDaytime+"的功率谱PDF图"
            data["spData"] = js14dict

            j = json.dumps(data,ensure_ascii=False,cls=MyEncoder)
            
            return Response(j,mimetype='application/json')

        elif methodName == "FDst" :

            startDaytime =  startTime + "_" + endTime

            hdffile = outputpath + 'FDst_WDCG_GLL_' + startDaytime + '_1Hour_Js.h5'

            if not os.path.exists(hdffile):

                cmdStr = IDLbatFDst + " " +filepath + " " + startDaytime + " " + outputpath + " " + str(timess) + " " + str(win_envss)
                os.system(cmdStr)

            localtimes = time.time()
            pngfile = outputpath + str(localtimes) + "_" +startDaytime + "_FDst_Js.png"
            Dst_jsPicture(hdffile,pngfile)

            DataName = "JS_Dst"
            kLineDatalist,Time123List,JS_Dstlist1 = KLineDataCalculate(startTime,endTime,DataName,hdffile)
            group1list,group2list = PowerPDFpicture(hdffile)

            data = {}
            datalist = []
            data["dataTypeKey"] = 'FDst'
            data["handelKey"] = product
            dataNameList1=[]
            dataNameList1.append(os.path.basename(filepath))
            data["dataNameList"] = dataNameList1

            js11dict = {}
            js11dict["name"] = methodName+ " " +startDaytime+"的Js指数计算结果"

            abs_path = os.path.abspath(pngfile)
            js11dict['stream_url'] = url_for('PNGStream', DataPath=abs_path)
            js11dict['download_url'] = url_for('PNGDownLoad', DataPath=abs_path)
            datalist.append(js11dict)
            data["imgList"] = datalist

            js12dict = {}
            js12dict["xData"] = Time123List
            js12dict["yData"] = JS_Dstlist1
            js12dict["name"] = methodName+ " " +startDaytime+"的Js指数计算结果"
            data["LineData"] = js12dict

            js13dict = {}
            js13dict["data"] = kLineDatalist
            js13dict["name"] = methodName+ " " + startDaytime+"的Js指数K线图"
            data["kLineData"] = js13dict

            js14dict = {}
            js14dict["group1"] = group1list
            js14dict["group2"] = group2list
            js14dict["name"] = methodName+ " " + startDaytime+"的功率谱PDF图"
            data["spData"] = js14dict

            j = json.dumps(data,ensure_ascii=False,cls=MyEncoder)
            
            return Response(j,mimetype='application/json')

        elif methodName == "RDst" :

            startDaytime = startTime + "_" + endTime

            hdffile = outputpath + 'RDst_WDCG_GLL_' + startDaytime + '_1Hour_Js.h5'

            if not os.path.exists(hdffile):

                cmdStr = IDLbatRDst + " " +filepath + " " + startDaytime + " " + outputpath + " " + str(timess) + " " + str(win_envss)
                os.system(cmdStr)

            localtimes = time.time()
            pngfile = outputpath + str(localtimes) + "_" +startDaytime + "_RDst_Js.png"
            Dst_jsPicture(hdffile,pngfile)

            DataName = "JS_Dst"
            kLineDatalist,Time123List,JS_Dstlist1 = KLineDataCalculate(startTime,endTime,DataName,hdffile)
            group1list,group2list = PowerPDFpicture(hdffile)

            data = {}
            datalist = []
            data["dataTypeKey"] = 'RDst'
            data["handelKey"] = product
            dataNameList1=[]
            dataNameList1.append(os.path.basename(filepath))
            data["dataNameList"] = dataNameList1

            js11dict = {}
            js11dict["name"] = methodName+ " " + startDaytime+"的Js指数计算结果"

            abs_path = os.path.abspath(pngfile)
            js11dict['stream_url'] = url_for('PNGStream', DataPath=abs_path)
            js11dict['download_url'] = url_for('PNGDownLoad', DataPath=abs_path)
            datalist.append(js11dict)
            data["imgList"] = datalist

            js12dict = {}
            js12dict["xData"] = Time123List
            js12dict["yData"] = JS_Dstlist1
            js12dict["name"] = methodName+ " " + startDaytime+"的Js指数计算结果"
            data["LineData"] = js12dict

            js13dict = {}
            js13dict["data"] = kLineDatalist
            js13dict["name"] = methodName+ " " + startDaytime+"的Js指数K线图"
            data["kLineData"] = js13dict

            js14dict = {}
            js14dict["group1"] = group1list
            js14dict["group2"] = group2list
            js14dict["name"] = methodName+ " " + startDaytime+"的功率谱PDF图"
            data["spData"] = js14dict

            j = json.dumps(data,ensure_ascii=False,cls=MyEncoder)
            
            return Response(j,mimetype='application/json')


class PNGStream(Resource):

    def get(self):
        data_abs_path = request.args.get('DataPath')
        dir_name = os.path.dirname(data_abs_path)
        file_name = os.path.basename(data_abs_path)
        return send_from_directory(dir_name, file_name)


class PNGDownLoad(Resource):

    def get(self):
        data_abs_path = request.args.get('DataPath')
        dir_name = os.path.dirname(data_abs_path)
        file_name = os.path.basename(data_abs_path)
        return send_from_directory(dir_name, file_name, as_attachment=True)


api.add_resource(PNGStream, '/PNGStream', endpoint='PNGStream')
api.add_resource(PNGDownLoad, '/PNGDownLoad', endpoint='PNGDownLoad')
api.add_resource(PNGINFO, '/PNGINFO')


if __name__ == '__main__':
    # app.run(debug=True)
    CORS(app, supports_credentials=True)
    # http_server = WSGIServer(('0.0.0.0', 5002), app)
    http_server = WSGIServer(('0.0.0.0', 8888), app)
    http_server.serve_forever()



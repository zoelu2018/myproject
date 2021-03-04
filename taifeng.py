# coding:utf-8

import os
import sys
import re
import json
import requests
# import datetime
from datetime import datetime,timedelta

# import config
from MysqlHelper import MySQLHelper


DBHOST='121.36.13.81'
DBPORT=3306
DBUSER='fy4'
DBPASSWD='fy4'
DBNAME='taifeng'
TBNAME='typhoon'

baseURL = 'http://typhoon.nmc.cn/weatherservice/typhoon/jsons/view_{0}?t={1}&callback=typhoon_jsons_view_{0}'

def covertDegree(az):
    if 'N' == az:
        return 360
    elif 'NE' == az:
        return 45
    elif 'E' == az:
        return 90
    elif 'SE' == az:
        return 135
    elif 'S' == az:
        return 180
    elif 'SW' == az:
        return 225
    elif 'W' == az:
        return 270
    elif 'NW' == az:
        return 315
    elif 'NNE' == az:
        return 22.5
    elif 'ENE' == az:
        return 67.5
    elif 'ESE' == az:
        return 112.5
    elif 'SSE' == az:
        return 157.5
    elif 'SSW' == az:
        return 202.5
    elif 'WSW' == az:
        return 247.5
    elif 'WNW' == az:
        return 292.5
    elif 'NNW' == az:
        return 337.5
    else:
        return 0

def parseURL(url):
    '''
    解析 url , 并获取其中的数据 
    '''
    
    res = requests.get(url)

    print res.status_code

    # with open('taifeng.txt','w') as fp :

    #     fp.write(res.content)

    typhoon_json = json.loads(re.split(r'[()]',res.content)[1])

    return typhoon_json

def insertDB(record):

    '''
    数据入库
    '''

    sqlHelper = MySQLHelper(DBHOST,DBPORT,DBUSER,DBPASSWD,DBNAME,TBNAME)

    typhoon_id = record[0]    # 台风ID号
    typhoon_en = record[1]    # 台风英文名
    typhoon_cn = record[2]    # 台风中文名

    typhoon_no1 = record[3]    # 台风编号
    typhoon_no2 = record[4]    # 台风编号
    typhoon_date = record[5]    # 台风日期
    typhoon_des = record[6]    # 台风含义
    typhoon_status = record[7]    # 台风状态
    typhoon_points = record[8]    # 台风轨迹

    for tp_child in typhoon_points:

        # 观测点的ID
        tp_child_id = tp_child[0]
        # 观测点的时间（UTC）
        tp_child_dt = tp_child[1]
        # 观测点距离（1970.1.1）的毫秒计数
        tp_child_dist = tp_child[2]
        # 观测点台风的强度
        tp_child_strenght = tp_child[3]
        # 观测点的经度
        tp_child_lon = tp_child[4]
        # 观测点的纬度
        tp_child_lat = tp_child[5]
        # 观测点的中心气压
        tp_child_bpa = tp_child[6]
        # 观测点的最大风速 m/s
        tp_child_speed = tp_child[7]
        # 观测点的移动方向
        tp_child_direct = tp_child[8]
        # 观测点的移动速度
        tp_child_move = tp_child[9]

        # 风圈半径
        winds = dict()
        winds['30KTS'] = [999999,99999,999999,999999,999999,99999,999999,999999]
        winds['50KTS'] = [999999,99999,999999,999999,999999,99999,999999,999999]
        winds['64KTS'] = [999999,99999,999999,999999,999999,99999,999999,999999]

        for wind in tp_child[10]:
            winds[wind[0]][4:8] = wind[1:5]

        # 解析预测结果
        tp_forecasts = tp_child[11]['BABJ']

        for tp_forecast in tp_forecasts:
            sql_str = ("replace into {0}(Datetime,Bul_Center,TYPH_Name,Typh_Grade,Num_Nati,Num_INati,Validtime_Count,Validtime,Lat,Lon,PRS,WIN_S_Gust_Max,WIN_S_Conti_Max,\
                        WING_A7_Bear1,Radiu_Bear1_WING_A7,WING_A7_Bear2,Radiu_Bear2_WING_A7,WING_A7_Bear3,Radiu_Bear3_WING_A7,WING_A7_Bear4,Radiu_Bear4_WING_A7,\
                        WING_A10_Bear1,Radiu_Bear1_WING_A10,WING_A10_Bear2,Radiu_Bear2_WING_A10,WING_A10_Bear3,Radiu_Bear3_WING_A10,WING_A10_Bear4,Radiu_Bear4_WING_A10,\
                        WING_A12_Bear1,Radiu_Bear1_WING_A12,WING_A12_Bear2,Radiu_Bear2_WING_A12,WING_A12_Bear3,Radiu_Bear3_WING_A12,WING_A12_Bear4,Radiu_Bear4_WING_A12,\
                        MoDir_Future,MoSpeed_Futrue,TYPH_Name_cn\
                        ) values ('{1}','{2}','{3}','{4}',{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21},{22},{23},{24},{25},\
                                    {26},{27},{28},{29},{30},{31},{32},{33},{34},{35},{36},{37},{38},{39},'{40}')".format(TBNAME,str(datetime.strptime(tp_child_dt,'%Y%m%d%H%M%S') + timedelta(hours=-8)),'BABJ',typhoon_en,tp_forecast[7],typhoon_no1,typhoon_no2,
                            len(tp_forecasts)+1,tp_forecast[0],tp_forecast[3],tp_forecast[2],tp_forecast[4],999999,tp_child_speed,
                            winds['30KTS'][0],winds['30KTS'][4],winds['30KTS'][1],winds['30KTS'][5],winds['30KTS'][2],winds['30KTS'][6],winds['30KTS'][3],winds['30KTS'][4],
                            winds['50KTS'][0],winds['50KTS'][4],winds['50KTS'][1],winds['50KTS'][5],winds['50KTS'][2],winds['50KTS'][6],winds['50KTS'][3],winds['50KTS'][4],
                            winds['64KTS'][0],winds['64KTS'][4],winds['64KTS'][1],winds['64KTS'][5],winds['64KTS'][2],winds['64KTS'][6],winds['64KTS'][3],winds['64KTS'][4],
                            covertDegree(tp_child_direct.encode('utf-8')), float(tp_forecast[5])/3.6,typhoon_cn.encode('gb2312')
                        ))

            # print sql_str

            sqlHelper.Insert(sql_str)

        
        sql_str = ("replace into {0}(Datetime,Bul_Center,TYPH_Name,Typh_Grade,Num_Nati,Num_INati,Validtime_Count,Validtime,Lat,Lon,PRS,WIN_S_Gust_Max,WIN_S_Conti_Max,\
                    WING_A7_Bear1,Radiu_Bear1_WING_A7,WING_A7_Bear2,Radiu_Bear2_WING_A7,WING_A7_Bear3,Radiu_Bear3_WING_A7,WING_A7_Bear4,Radiu_Bear4_WING_A7,\
                    WING_A10_Bear1,Radiu_Bear1_WING_A10,WING_A10_Bear2,Radiu_Bear2_WING_A10,WING_A10_Bear3,Radiu_Bear3_WING_A10,WING_A10_Bear4,Radiu_Bear4_WING_A10,\
                    WING_A12_Bear1,Radiu_Bear1_WING_A12,WING_A12_Bear2,Radiu_Bear2_WING_A12,WING_A12_Bear3,Radiu_Bear3_WING_A12,WING_A12_Bear4,Radiu_Bear4_WING_A12,\
                    MoDir_Future,MoSpeed_Futrue,TYPH_Name_cn\
                    ) values ('{1}','{2}','{3}','{4}',{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21},{22},{23},{24},{25},\
                                {26},{27},{28},{29},{30},{31},{32},{33},{34},{35},{36},{37},{38},{39},'{40}')".format(TBNAME,str(datetime.strptime(tp_child_dt,'%Y%m%d%H%M%S') + timedelta(hours=-8)),'BABJ',typhoon_en,tp_child_strenght,typhoon_no1,typhoon_no2,
                        len(tp_forecasts)+1,0,tp_child_lat,tp_child_lon,tp_child_bpa,999999,tp_child_speed,
                        winds['30KTS'][0],winds['30KTS'][4],winds['30KTS'][1],winds['30KTS'][5],winds['30KTS'][2],winds['30KTS'][6],winds['30KTS'][3],winds['30KTS'][4],
                        winds['50KTS'][0],winds['50KTS'][4],winds['50KTS'][1],winds['50KTS'][5],winds['50KTS'][2],winds['50KTS'][6],winds['50KTS'][3],winds['50KTS'][4],
                        winds['64KTS'][0],winds['64KTS'][4],winds['64KTS'][1],winds['64KTS'][5],winds['64KTS'][2],winds['64KTS'][6],winds['64KTS'][3],winds['64KTS'][4],
                        covertDegree(tp_child_direct.encode('utf-8')), float(tp_child_move)/3.6,typhoon_cn.encode('gb2312')
                    ))

        # print sql_str
        sqlHelper.Insert(sql_str)

if __name__ == "__main__":

    # tf_id =  sys.argv[1]

    # 海神

    tf_ids = sys.argv[1].split(',')

    for tf_id in tf_ids:
        
        t1 = datetime.now()
        t2 = datetime(1970,1,1)

        t = ((t1 - t2).total_seconds()) * 1000

        print 'total seconds : ',t

        url = baseURL.format(tf_id,t)

        typhoon_json = parseURL(url)

        insertDB(typhoon_json['typhoon'])

    print 'done'

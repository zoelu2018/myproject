import sys
import os
import pandas as pd
import numpy as np
import csv
def opencsv():
    # data = pd.read_csv('D:/TSBrowserDownloads/DL_FIRE_J1V-C2_142990/fire_nrt_J1V-C2_142990.csv')
    # datat = pd.to_datetime(data['acq_data'])
    data1 = pd.read_csv('D:/TSBrowserDownloads/DL_FIRE_J1V-C2_175654/fire_nrt_J1V-C2_175654.csv',
                        usecols=['latitude',
                                'longitude',
                                'acq_date'])
    date_list = data1['acq_date'].unique()# 搜索唯一值
    for date_str in date_list:
        time = date_str
        time = time.replace("-",'')
        path ='D:/TSBrowserDownloads/DL_FIRE_J1V-C2_175654/result/'+'FP_'+'NPP_'+'VIIRS_'+'LatLon_'+'L2_'+time+'_0750M'+'.TXT'
        cursor = data1[data1['acq_date'] == date_str]
        data11 = cursor[['latitude', 'longitude']]
        # data11.reset_index().rename(columns={"index":"xuhao"})
        # data11.to_csv(path,sep='\t',index=True)
        temp = np.array(data11)
        file_handle = open(path, 'w')
        file_handle.write("xuhao"+" "+"Lat"+" "+"Lon"+'\n') # 写列名
        for i in range(temp.shape[0]):
            index=i+1
            serise = str(index)+" "+str(temp[i,0])+" "+str(temp[i,1]) # 每个元素都是字符串，使用逗号分割拼接成一个字符串
            file_handle.write(serise+'\n') # 末尾使用换行分割每一行。
        file_handle.close()
        # cursor[['latitude', 'longitude']].to_txt(path, index = index+1)
        
if __name__ == '__main__':

    opencsv()
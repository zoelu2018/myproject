#!/usr/bin/env python
# -*- coding:utf-8 -*-
import h5py
#from pyhdf import SD
import numpy as np
import time
import datetime
import sys
import os
AVHRRInFileName = "/FY3/AVHRR/DAILY/YYYY/NOAA15_AVHRR_GBAL_L2_ASC_GLL_YYYYMMDD_AOAD_010D_MS.HDF"
AVHRRInmonthFileName =  "/FY3/AVHRR/MONTHLY/NOAA15_AVHRR_GBAL_L3_ASC_GLL_YYYYMMDD_yyyymmdd_AOAM_010D_MS.HDF"
#sdsname = "AOD"
#modisAODFileName = "E:/AOD/2015resultD/TERRA_MODIS_Latlon_L2_AOD_XXX_YYYYMMDD_3000M_Latlon_POAD_D.HDF"
#modisAODmonthFileName = "E:/AOD/2015resultD/TERRA_MODIS_Latlon_L3_AOD_YYYYMM_3000M_Latlon_POAM_D.HDF"
#/data/dbwarehourse/modis/input/产品名（例如LST）/年份（2018）/2018result/内
filenamemonout =  "/FY3/AVHRR/MONTHLY/NOAA15_AVHRR_GBAL_L3_ASC_GLL_YYYYMMDD_yyyymmdd_AOAM_010D_MS.HDF"
filenameyearout = "/FY3/AVHRR/YEARLY/NOAA15_AVHRR_GBAL_L3_ASC_GLL_YYYYMMDD_yyyymmdd_AOAY_010D_MS.HDF"
m_sdsname = ["cloud_mask","cloud_fraction","cloud_type","cld_temp_acha","cld_height_acha","cld_press_acha","cld_reff_acha","cld_reff_dcomp","cld_opd_acha","cld_opd_dcomp"]
def ReadData_HDF5(FileName, SDSName):
	with h5py.File(FileName, 'r') as File:
		data = File[SDSName]
		slope = data.attrs['Slope']
		avhrr_data = data.value
		attrs = {}
		for key in data.attrs.keys():
			attrs.update({key:data.attrs[key]})
	return attrs,avhrr_data
	
# def readdata(FileName, SDSName):
	# hdf_obj = SD.SD(FileName, SD.SDC.READ)
	# data = hdf_obj.select(SDSName)
	# slope = data.__getattr__('scale_factor')
	# datavalue = data.get() * slope
	# print (data.attributes())
	# return data.attributes(),datavalue
	
def WriteData(strFileName, SDSName, data, Attri, Overwrite):
	print (strFileName)
	dirs = os.path.dirname(strFileName)
	if not os.path.exists(dirs):
		os.makedirs(dirs)
	data = np.array(data)
	size = data.shape
	type = data.dtype


	#print size
	if Overwrite == 1:
		fout = h5py.File(strFileName, "w") #创建，写文件属性
		# fout[SDSName]=Data
		fout.attrs['AdditionalAnnotation'] = 'ShineTek Co.,Ltd'
		fout.attrs['CenterPoint Latitude'] = 0.0
		fout.attrs['CenterPoint Longitude'] = 0.0
		fout.attrs['Data Date'] = time.strftime('%Y-%m-%d',time.localtime(time.time()))
		fout.attrs['Data Level'] = 'L3'
		fout.attrs['Data Set'] = 'AOD'
		fout.attrs['Data Time'] = time.strftime('%H:%M:%S',time.localtime(time.time()))
		fout.attrs['Day Or Night Flag'] = 'D'
		fout.attrs['File Name'] = strFileName
		fout.attrs['Latitude Precision'] = 0.1
		fout.attrs['Longitude Precision'] = 0.1
		fout.attrs['Maximum Latitude'] = 90.0
		fout.attrs['Maximum Longitude'] = 180.0
		fout.attrs['Maximum X'] = 180.0
		fout.attrs['Maximum Y'] = 90.0
		fout.attrs['Minimum Latitude'] = -90.0
		fout.attrs['Minimum Longitude'] = -180.0
		fout.attrs['Minimum X'] = -180.0
		fout.attrs['Minimum Y'] = -90.0
		fout.attrs['Orbit Direction'] = 'A'
		fout.attrs['Piexl Height'] = size[0]
		fout.attrs['Piexl Width'] = size[1]
		fout.attrs['Product Name '] = 'AOD'
		fout.attrs['Projection Center Longitude'] = 0.0
		fout.attrs['Projection Type'] = ' Latlon'
		fout.attrs['Satellite Name'] = 'NOAA'
		fout.attrs['Sensor Name'] = 'AVHRR'
		fout.attrs['Standard Latitude 1'] = 0.0
		fout.attrs['Standard Latitude 2'] = 0.0
		fout.attrs['x_0'] = 0
		fout.attrs['y_0'] = 0
	else:
		fout = h5py.File(strFileName, "a")  #追加
		
	dset = fout.create_dataset(name=SDSName, shape=size, dtype='int16', data=data)
	for key in Attri.keys():
		dset.attrs[key] = Attri[key]
	fout.close()

def mean_month(outfilename,sdsname,date0,days,year,Overwrite):
	resultdata = []
	resultquality = []
	symbolfile = 0
	for day in range(0,days,1):
		date = date0 + day
		FileName =  AVHRRInFileName.replace('YYYYMMDD', str(date)).replace('YYYY',str(year))
		#FileName =  AVHRRInFileName.replace('YYYYMMDD', str(date))
		
		print (FileName,sdsname)
		#attr,avhrr_data = readdata(FileName, sdsname)
		if(os.path.isfile(FileName)):
			attr, avhrr_data = ReadData_HDF5(FileName, sdsname)
			if symbolfile == 0:
				resultdata = np.zeros(avhrr_data.shape)
				resultquality = np.zeros(avhrr_data.shape)
			symbolfile = symbolfile + 1
		else:
			print("file not exist")
			continue
		#print (attr['valid_range'][0])
		avhrr_data = np.array(avhrr_data)
		dataquality = np.zeros(avhrr_data.shape)
		#valmask = (avhrr_data >= -100) & (avhrr_data <= 5000)
		valmask = (avhrr_data >= attr['valid_range'][0]) & (avhrr_data <= attr['valid_range'][1])
		dataquality[valmask] = 1
		dataquality[~valmask] = 0
		avhrr_data[~valmask] = 0
		resultdata += avhrr_data
		resultquality += dataquality
	print('exist file:%d'%symbolfile)
	if symbolfile == 0:
		exit(0)
	valmask = resultquality != 0
	resultdata[valmask] = resultdata[valmask] * 1.0 / resultquality[valmask]
	maskfill = resultdata == 0
	resultdata[maskfill] = attr['_FillValue']
	WriteData(outfilename,sdsname,resultdata,attr,Overwrite)

def percent_month(outfilename,sdsname,date0,days,year,weidu,Overwrite):
	resultdata = []

	symbolfile = 0
	dataflag=0  ##用于标记第一个存在的文件，定义输出数组维度
	
	for day in range(0,days,1):
		date = date0 + day
		FileName =  AVHRRInFileName.replace('YYYYMMDD', str(date)).replace('YYYY',str(year))
		#FileName =  AVHRRInFileName.replace('YYYYMMDD', str(date))
		
		print (FileName,sdsname)
		if(os.path.isfile(FileName)):
			attr, avhrr_data = ReadData_HDF5(FileName, sdsname)
			if dataflag == 0 :
				height,width = avhrr_data.shape
				resultdata=np.zeros((weidu+1,height,width))
				sumdata=np.zeros((weidu,height,width))

			symbolfile = symbolfile + 1
		else:
			print("file not exist")
			continue
		#print (attr['valid_range'][0])
		avhrr_data = np.array(avhrr_data)
		#valmask = (avhrr_data >= attr['valid_range'][0]) & (avhrr_data <= attr['valid_range'][1])
		for num in range(0,weidu,1):
			print(num)
			mask = avhrr_data == num
			sumdata[num][mask] += 1
		
	print('exist file:%d'%symbolfile)
	if symbolfile == 0:
		exit(0)
	for nn in range(0,weidu,1):
		resultdata[weidu] += sumdata[nn]
	mask = resultdata[weidu] != 0
	maskfill = resultdata[weidu] == 0
	resultdata[0][mask] = 100*sumdata[0][mask]/resultdata[weidu][mask]
	resultdata[0][maskfill] = attr['_FillValue']
	for nn in range(1,weidu,1):
		mask1 = resultdata[weidu] - sumdata[0] != 0
		masknn = mask & mask1
		resultdata[nn][masknn] = 100*sumdata[nn][masknn]/(resultdata[weidu][masknn]-sumdata[0][masknn])
		resultdata[nn][maskfill] = attr['_FillValue']
	resultdata[weidu][maskfill] = attr['_FillValue']
	WriteData(outfilename,sdsname,resultdata,attr,Overwrite)


def mean_year(outfilename,sdsname,date0,monthdays,year,Overwrite):
	resultdata = []
	resultquality = []
	symbolfile = 0
	for mon in range(0,12,1):
		date = int(date0) + mon
		sdate = str(date) + '01'
		edate = str(date) + str(monthdays[mon])
		#FileName =  AVHRRInmonthFileName.replace('YYYYMMDD', sdate).replace('YYYY',str(year)).replace('yyyymmdd',edate)
		FileName =  AVHRRInmonthFileName.replace('YYYYMMDD', sdate).replace('yyyymmdd',edate)
		print (FileName,sdsname)
		if (os.path.isfile(FileName)):
			attr, avhrr_data = ReadData_HDF5(FileName, sdsname)
			if symbolfile == 0:
				resultdata = np.zeros(avhrr_data.shape)
				resultquality = np.zeros(avhrr_data.shape)
			symbolfile = symbolfile + 1
		else:
			print("file not exist")
			continue

		avhrr_data = np.array(avhrr_data)
		dataquality = np.zeros(avhrr_data.shape)
		valmask = (avhrr_data >= attr['valid_range'][0]) & (avhrr_data <= attr['valid_range'][1])
		dataquality[valmask] = 1
		dataquality[~valmask] = 0
		avhrr_data[~valmask] = 0
		resultdata += avhrr_data
		resultquality += dataquality
	print ('exist file is {}'.format(symbolfile))
	valmask = resultquality != 0
	resultdata[valmask] = resultdata[valmask] * 1.0 / resultquality[valmask]
	maskfill = resultdata == 0
	resultdata[maskfill] = attr['_FillValue']
	WriteData(outfilename,sdsname,resultdata,attr,Overwrite)

def percent_year(outfilename,sdsname,date0,monthdays,year,weidu,Overwrite):
	resultdata = []
	resultquality = []
	symbolfile = 0
	for mon in range(0,12,1):
		date = int(date0) + mon
		sdate = str(date) + '01'
		edate = str(date) + str(monthdays[mon])
		#FileName =  AVHRRInmonthFileName.replace('YYYYMMDD', sdate).replace('YYYY',str(year)).replace('yyyymmdd',edate)
		FileName =  AVHRRInmonthFileName.replace('YYYYMMDD', sdate).replace('yyyymmdd',edate)
		print (FileName,sdsname)
		if (os.path.isfile(FileName)):
			attr, avhrr_data = ReadData_HDF5(FileName, sdsname)
			if symbolfile == 0:
				resultdata = np.zeros(avhrr_data.shape)
				sumdata = np.zeros(avhrr_data.shape)
			symbolfile = symbolfile + 1
		else:
			print("file not exist")
			continue

		#avhrr_data = np.array(avhrr_data)
		valmask = (avhrr_data[weidu] != attr['_FillValue'])
		sumdata[weidu][valmask] += avhrr_data[weidu][valmask]
		sumdata[0][valmask] += (avhrr_data[0][valmask]*avhrr_data[weidu][valmask]/100)
		for nn in range(1,weidu,1):
			sumdata[nn][valmask] += ((avhrr_data[weidu][valmask]-avhrr_data[0][valmask]*avhrr_data[weidu][valmask]/100)*avhrr_data[nn][valmask]/100)
			
	print ('exist file is {}'.format(symbolfile))
	
	resultdata[weidu]=sumdata[weidu]
	mask = resultdata[weidu] != 0
	maskfill = resultdata[weidu] == 0
	resultdata[0][mask] = 100*sumdata[0][mask]/resultdata[weidu][mask]
	resultdata[0][maskfill] = attr['_FillValue']
	for nn in range(1,weidu,1):
		mask1 = resultdata[weidu] - sumdata[0] != 0
		masknn = mask & mask1
		resultdata[nn][masknn] = 100*sumdata[nn][masknn]/(resultdata[weidu][masknn]-sumdata[0][masknn])
		resultdata[nn][maskfill] = attr['_FillValue']
	resultdata[weidu][maskfill] = attr['_FillValue']

	WriteData(outfilename,sdsname,resultdata,attr,Overwrite)


def compose_month(date1,date22):
	print(date1)
	stime = datetime.datetime.strptime(date1, '%Y%m%d')
	stime += datetime.timedelta(days=32)
	stime -= datetime.timedelta(days=stime.day)
	print(stime)

	date2 = datetime.datetime.strftime(stime, '%Y%m%d')
	month = date1[4:6]
	year = date1[0:4]
	monthdays = [31,28,31,30,31,30,31,31,30,31,30,31]
	days = monthdays[int(month)-1]
	date0 = int(date1)
	#FileName = AVHRRInFileName.replace('YYYYMMDD', str(date0)).replace('YYYY',str(year))
	FileName = AVHRRInFileName.replace('YYYYMMDD', date1)
	print(FileName)
	#date2 = str(year) + str(month) + str(days+1)
	#outfilename = filenamemonout.replace('YYYYMMDD', str(date0)).replace('YYYY',year).replace('yyyymmdd',str(date2))
	outfilename = filenamemonout.replace('YYYYMMDD', date1).replace('yyyymmdd',str(date2))
	print ('out:',outfilename, date2)
	#exit(0)

	#云量
	mean_month(outfilename,m_sdsname[1],date0,days,year,1)
	#云顶温度
	mean_month(outfilename,m_sdsname[3],date0,days,year,0)
	#云顶高度
	mean_month(outfilename,m_sdsname[4],date0,days,year,0)
	#云顶气压
	mean_month(outfilename,m_sdsname[5],date0,days,year,0)
	#云有效粒子半径ACHA
	mean_month(outfilename,m_sdsname[6],date0,days,year,0)
	#云有效粒子半径DCOMP
	mean_month(outfilename,m_sdsname[7],date0,days,year,0)
	#云光学厚度ACHA
	mean_month(outfilename,m_sdsname[8],date0,days,year,0)
	#云光学厚度DCOMP
	mean_month(outfilename,m_sdsname[9],date0,days,year,0)
	
	#云检测
	percent_month(outfilename,m_sdsname[0],date0,days,year,4,0)
	#云分类
	percent_month(outfilename,m_sdsname[2],date0,days,year,13,0)
	
	

def compose_year(date1,date2):
	#print date1
	stime = datetime.datetime.strptime(date1, '%Y%m%d')
	month = date1[4:6]
	year = date1[0:4]
	monthdays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	days = monthdays[int(month) - 1]
	date0 = year + month
	date00 =  year + month + str(days)
	#FileName = AVHRRInmonthFileName.replace('YYYYMMDD', date1).replace('YYYY',str(year)).replace('yyyymmdd',date00)
	FileName = AVHRRInmonthFileName.replace('YYYYMMDD', date1).replace('yyyymmdd',date00)
	#date2 = year
	outfilename = filenameyearout.replace('YYYYMMDD', date1).replace('yyyymmdd',date2)
	print (FileName,date1,date2)

	#云量
	mean_year(outfilename,m_sdsname[1],date0,monthdays,year,1)
	#云顶温度
	mean_year(outfilename,m_sdsname[3],date0,monthdays,year,0)
	#云顶高度
	mean_year(outfilename,m_sdsname[4],date0,monthdays,year,0)
	#云顶气压
	mean_year(outfilename,m_sdsname[5],date0,monthdays,year,0)
	#云有效粒子半径ACHA
	mean_year(outfilename,m_sdsname[6],date0,monthdays,year,0)
	#云有效粒子半径DCOMP
	mean_year(outfilename,m_sdsname[7],date0,monthdays,year,0)
	#云光学厚度ACHA
	mean_year(outfilename,m_sdsname[8],date0,monthdays,year,0)
	#云光学厚度DCOMP
	mean_year(outfilename,m_sdsname[9],date0,monthdays,year,0)
	
	#云检测
	percent_year(outfilename,m_sdsname[0],date0,monthdays,year,4,0)
	#云分类
	percent_year(outfilename,m_sdsname[2],date0,monthdays,year,13,0)


if __name__ == '__main__':
	startdate = sys.argv[1]
	enddate = sys.argv[2]
	producemod = sys.argv[3]
	if  producemod == "M":
		compose_month(startdate,enddate)
	if  producemod == "Y":
		compose_year(startdate,enddate)
		
	print (time.strftime('%Y.%m.%d.%H.%M.%S', time.localtime(time.time())))

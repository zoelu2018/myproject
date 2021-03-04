# -*- coding: utf-8 -*-
from DataProvider import *
from CORE.HdfOperator import *
import numpy as N

class FY3D_MERSI_Provider(DataProvider):

    def __init__(self):
        super(FY3D_MERSI_Provider, self).__init__()
        self.__HdfFileHandleList = dict()
        self.__description = 'NULL'
        self.__BandWaveLenthList = None
        self.__HdfOperator = HdfOperator()
        self.__ProjResolution = 0

        self.__AuxiliaryDataNamesDict = dict()
        self.__BandWaveDataNamesDict = dict()

        return

    def Dispose(self):
        self.__AuxiliaryDataNamesList.clear()
        if self.__BandWaveLenthList is not None:
            del self.__BandWaveLenthList
            self.__BandWaveLenthList = None

        for filehandleName in self.__HdfFileHandleList:
            filehandle = self.__HdfFileHandleList[filehandleName]
            if filehandle.id.valid:
                filehandle.close()

        self.__HdfFileHandleList.clear()

        self.__description = 'NULL'
        super(FY3D_MERSI_Provider, self).Dispose()

    def __InitOrbitInfo(self):
        pass

    def __InitBandsNameDict(self,bandIndex):
        """
        初始化波段数据集对照表
        :param bandIndex: 波段序号
        :return:
        """

        if bandIndex in range(1,5):
            dataSetName = "Data/EV_250_Aggr.1KM_RefSB"
            # 指定三维数组中的哪一维
            index = bandIndex - 1

        elif bandIndex in range(5,20):
            dataSetName = "Data/EV_1KM_RefSB"
            index = bandIndex - 5

        elif bandIndex in range(20,24):
            dataSetName = "Data/EV_1KM_Emissive"
            index = bandIndex - 20

        elif bandIndex in range(24,26):
            dataSetName = "Data/EV_250_Aggr.1KM_Emissive";
            index = bandIndex - 24

        # 对于250M投影的区别
        if int(self.__ProjResolution) < 1000:
            if bandIndex in range(1,5):
                dataSetName = "Data/EV_250_RefSB_b" + str(bandIndex)
                # 指定三维数组中的哪一维
                index = -1
            elif bandIndex in range(24,26):
                dataSetName = "Data/EV_250_Emissive_b" + str(bandIndex)
                # 指定三维数组中的哪一维
                index = -1

        self.__BandWaveDataNamesDict[bandIndex] = [dataSetName, index]

    def __InitAuxiliarysNameDict(self, auxiliaryName):

        """
        初始辅助数据集对照表
        :param auxiliaryName: 辅助数据集名称
        :return:
        """
        if 'LandCover' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'Geolocation/LandCover'
        elif 'Height' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'Geolocation/DEM'
        elif 'SensorAzimuth' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'Geolocation/SensorAzimuth'
        elif 'SensorZenith' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'Geolocation/SensorZenith'
        elif 'SolarAzimuth' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'Geolocation/SolarAzimuth'
        elif 'SolarZenith' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'Geolocation/SolarZenith'

    def GetDate(self):
        pass

    def GetTime(self):
        pass

    def OnParametersUpdate(self):

        self.__ProjResolution = self.GetParameter().ProjResolution
        self.IsATC = self.GetParameter().IsAtmosphere

        super(FY3D_MERSI_Provider, self).OnParametersUpdate()

        self.__BandWaveLenthList = self.GetParameter().BandWaveLengthList
        self.__AuxiliaryDataList = self.GetParameter().AuxiliaryDataList
        self.__CentralLenght=[470,550,650,865,1380,1640,2130,412,443,490,555,670,709,746,865,905,936,940,1030,3800,4050,7200,8550,10800,12000]

        self.OrbitInfo.Sat = 'FY3D'
        self.OrbitInfo.Sensor = 'MERSI'
        self.OrbitInfo.Date = self.GetParameter().TimeFlag[:8]
        self.OrbitInfo.Time = self.GetParameter().TimeFlag[8:]
        self.OrbitInfo.Wavelength = self.__CentralLenght

        self.OrbitInfo.Bands = []

        for i in range(len(self.__BandWaveLenthList)):
            self.OrbitInfo.Bands.append(i+1)

        for band in self.__BandWaveLenthList:

            index = int(band[8:])

            if 'REF' in band:
                self.OrbitInfo.BandsREF.append(self.__CentralLenght[index - 1])
            elif 'EMI' in band:
                self.OrbitInfo.BandsEMI.append(self.__CentralLenght[index - 1])

            self.__InitBandsNameDict(index)

        return

    def SetLonLatFile(self, latfile, lonfile):
        '''
        设置经纬度文件
        :param latfile: 纬度文件
        :param lonfile: 经度文件
        :return: none
        '''
        self.__HdfFileHandleList['Latitude'] = self.__HdfOperator.Open(latfile)
        self.__HdfFileHandleList['Longitude'] = self.__HdfOperator.Open(lonfile)

        if 'GEO1K' in latfile:
            self.__AuxiliaryDataNamesDict['Latitude'] = 'Geolocation/Latitude'
            self.__AuxiliaryDataNamesDict['Longitude'] = 'Geolocation/Longitude'
        else:
            self.__AuxiliaryDataNamesDict['Latitude'] = 'Latitude'
            self.__AuxiliaryDataNamesDict['Longitude'] = 'Longitude'

    def SetL1File(self, file):
        """
        设置L1文件
        :param file: L1输入文件
        :return:
        """
        self.__HdfFileHandleList['L1'] = self.__HdfOperator.Open(file)

    def SetATCFile(self,file):
        """
        设置大气校正文件
        :param file:  大气校正输入文件
        :return:
        """
        if os.path.exists(file):
            self.__HdfFileHandleList['ATC']=self.__HdfOperator.Open(file)

    def SetAuxilyFile(self,file):
        """
        设置辅助信息文件
        :param file:  辅助信息文件
        :return:
        """
        self.__HdfFileHandleList['Auxily']=self.__HdfOperator.Open(file)

        if 'GEO1K' in file:
            """
            初始辅助数据集对照表
            :param auxiliaryName: 辅助数据集名称
            :return:
            """
            self.__AuxiliaryDataNamesDict['LandSeaMask'] = 'Geolocation/LandSeaMask'
            self.__AuxiliaryDataNamesDict['Height'] = 'Geolocation/DEM'
            self.__AuxiliaryDataNamesDict['SensorAzimuth'] = 'Geolocation/SensorAzimuth'
            self.__AuxiliaryDataNamesDict['SensorZenith'] = 'Geolocation/SensorZenith'
            self.__AuxiliaryDataNamesDict['SolarAzimuth'] = 'Geolocation/SolarAzimuth'
            self.__AuxiliaryDataNamesDict['SolarZenith'] = 'Geolocation/SolarZenith'
        else:
            self.__AuxiliaryDataNamesDict['LandSeaMask'] = ''
            self.__AuxiliaryDataNamesDict['Height'] = ''
            self.__AuxiliaryDataNamesDict['SensorAzimuth'] = ''
            self.__AuxiliaryDataNamesDict['SensorZenith'] = ''
            self.__AuxiliaryDataNamesDict['SolarAzimuth'] = ''
            self.__AuxiliaryDataNamesDict['SolarZenith'] = ''

        return

    def GetLongitude(self):

        fileHandle = self.__HdfFileHandleList['Longitude']
        datasetName = self.__AuxiliaryDataNamesDict['Longitude']
        lon = fileHandle[datasetName].value
        return lon

    def GetLatitude(self):

        fileHandle = self.__HdfFileHandleList['Latitude']
        datasetName = self.__AuxiliaryDataNamesDict['Latitude']
        lat = fileHandle[datasetName].value
        return lat

    def GetOBSData(self, band):
        print "--> band wave name : ",band
        self.__bandwaveLength = band
        bandInfo = self.__BandWaveDataNamesDict[int(band[8:])]
        print bandInfo
        bandIndex = int(band[8:])
        datasetName = bandInfo[0]
        datasetIndex = bandInfo[1]
        ret = None
        if bandInfo != '':
            if self.IsATC==1 and bandIndex<18 and bandIndex!=5 and bandIndex!=13 and bandIndex!=15 and bandIndex!=16:
                # data = self.GetDataSet(self.__HdfFileHandleList['ATC'], '/', "CorrRefl_"+str(band[8:]).zfill(2))[:,:].astype(N.uint16)
                data = self.__HdfFileHandleList['ATC']["CorrRefl_"+str(band[8:]).zfill(2)].value.astype(N.float32)
                Slope = 0.1
                ret = data*Slope
                ret = ret.astype(N.int32)
                return ret
            else:
                fileHandle = self.__HdfFileHandleList['L1']
                if datasetIndex == -1:
                    data = fileHandle[datasetName].value.astype(N.float32)
                else:
                    data = fileHandle[datasetName].value[datasetIndex].astype(N.float32)
                attrs = self.__HdfFileHandleList['L1'][datasetName].attrs
                slopes = attrs["Slope"]
                ret = data * slopes[datasetIndex]

                if "Emi" in str(bandInfo[0]):
                    h = 6.62606876e-34 # Planck constant(Joule second)
                    c = 2.99792458e+8 # Speed of light in vacuum(meters per second)
                    k = 1.3806503e-23 # Boltzmann constant(Joules per
                    BandLength = self.__CentralLenght[bandIndex-1]

                    BandLength_um = float(BandLength)/1000 # nm convert to um
                    r = ret
                    EMIS_Mask =(ret<=0)
                    EMIS_Mask1=(ret==65535)
                    try:
                        r[EMIS_Mask] = 1
                    except:
                        pass

                    BandLength_m = BandLength_um/1000000  # convert to meter
                    C1 = 2*h*c*c
                    C2 = (h*c)/k
                    vs = 1/BandLength_m #Wavenumber inverse meters
                    ret = C2 * vs / N.log(C1 * (vs**3) / (1.0e-5 * r) + 1.0)
                    ret[EMIS_Mask] = 1
                    ret[EMIS_Mask1]=65535
                    ret = 10 * ret
                    ret = ret.astype(N.int32)
                    ret[ret==0]=65535
                else:
                    VIS_CAL_Coeff = self.__HdfFileHandleList['L1']['Calibration/VIS_Cal_Coeff'].value[datasetIndex].astype(N.float32)
                    ret=VIS_CAL_Coeff[0]+VIS_CAL_Coeff[1]*data+VIS_CAL_Coeff[2]*(data**2)
                    ret=ret*1000/100
                    ret[ret<=0]=1
                    ret = ret.astype(N.int32)

        print "--> get band data over :!"
        return ret

    def GetAuxiliaryData(self, auxilirayName):

        print ' --> auxiliary name :',auxilirayName

        fileHandle = self.__HdfFileHandleList['Auxily']
        dsname = self.__AuxiliaryDataNamesDict[auxilirayName]

        if dsname:
            auxiData = N.array(fileHandle[dsname].value)
            auxiData[auxiData==-32767] = 65535

            print "--> get auxiliary data over :!"
            return auxiData
        else:
            return None

    def GetAuxiliaryDataNamesList(self):
        return self.__AuxiliaryDataList

    def SetDataDescription(self, value):
        self.__description = value

    def GetDataDescription(self):
        if self.__description == 'NULL':
            self.__description = self.GetParameter().GetParamDescription() + '_' + str(
                self.GetParameter().ProjResolution)
        return self.__description

    def GetL1HandlelistAttr(self):
        attrs = self.__HdfFileHandleList['L1']["/"].attrs
        return attrs

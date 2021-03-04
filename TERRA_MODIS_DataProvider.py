# -*- coding: utf-8 -*-
from CORE.DataProvider.DataProvider import *
from CORE.h4Operate import *
from PIL import Image
import numpy as N
import math

class TERRA_MODIS_Provider(DataProvider):

    def __init__(self):
        super(TERRA_MODIS_Provider, self).__init__()
        self.__HdfFileHandleList = dict()
        self.__description = 'NULL'
        self.__BandWaveLenthList = None
        self.__HdfOperator = h4Operate()
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
        super(TERRA_MODIS_Provider, self).Dispose()

    def __InitOrbitInfo(self):
        pass

    def __InitBandsNameDict(self,bandIndex):
        """
        初始化波段数据集对照表
        :param bandIndex: 波段序号
        :return:
        """
        if bandIndex == 28:
            dataSetName = "EV_1KM_RefSB"
            index = 14

        elif bandIndex in range(1,3):
            dataSetName = "EV_250_Aggr1km_RefSB"
            # 指定三维数组中的哪一维
            index = bandIndex - 1

        elif bandIndex in range(3,8):
            dataSetName = "EV_500_Aggr1km_RefSB"
            index = bandIndex - 3

        elif bandIndex in range(8,22):
            dataSetName = "EV_1KM_RefSB"
            index = bandIndex - 8

        elif bandIndex in range(22,28):
            dataSetName = "EV_1KM_Emissive"
            index = bandIndex - 22

        elif bandIndex in range(29,39):
            dataSetName = "EV_1KM_Emissive"
            index = bandIndex - 23

        if int(self.__ProjResolution) < 1000 and int(self.__ProjResolution) >= 500:
            if bandIndex in range(1,3):
                dataSetName = "EV_250_Aggr500_RefSB"
                index = bandIndex - 1
            elif bandIndex in range(3,8):
                dataSetName = "EV_500_RefSB"
                # 指定三维数组中的哪一维
                index = bandIndex - 3

        elif int(self.__ProjResolution) < 500:
            if bandIndex in range(1,3):
                dataSetName = "EV_250_RefSB"
                index = bandIndex - 1
            elif bandIndex in range(3,8):
                dataSetName = "EV_500_RefSB"
                # 指定三维数组中的哪一维
                index = bandIndex - 3

        self.__BandWaveDataNamesDict[bandIndex] = [dataSetName, index]

    def __InitAuxiliarysNameDict(self, auxiliaryName):

        """
        初始辅助数据集对照表
        :param auxiliaryName: 辅助数据集名称
        :return:
        """
        if 'LandSeaMask' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'Land/SeaMask'
        elif 'Height' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'Height'
        elif 'SensorAzimuth' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'SensorAzimuth'
        elif 'SensorZenith' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'SensorZenith'
        elif 'SolarAzimuth' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'SolarAzimuth'
        elif 'SolarZenith' in auxiliaryName:
            self.__AuxiliaryDataNamesDict[auxiliaryName] = 'SolarZenith'

    def GetDate(self):
        pass

    def GetTime(self):
        pass

    def OnParametersUpdate(self):

        self.__ProjResolution = int(self.GetParameter().ProjResolution)
        self.IsATC = self.GetParameter().IsAtmosphere

        self.__AuxiliaryDataNamesDict['Latitude'] = 'Latitude'
        self.__AuxiliaryDataNamesDict['Longitude'] = 'Longitude'

        super(TERRA_MODIS_Provider, self).OnParametersUpdate()

        self.__BandWaveLenthList = self.GetParameter().BandWaveLengthList
        self.__AuxiliaryDataList = self.GetParameter().AuxiliaryDataList
        self.__CentralLenght=[620,841,459,545,1230,1628,2105,405,438,483,526,546,662,662,673,673,743,862,890,931,915,3660,
                              3930,3930,4020,4430,4480,1360,6530,7170,8400,9580,1078,1177,1318,1348,1378,1408]

        self.OrbitInfo.Sat = 'TERRA'
        self.OrbitInfo.Sensor = 'MODIS'
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

        for auxilyName in self.__AuxiliaryDataList:

            self.__InitAuxiliarysNameDict(auxilyName)

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
        if os.path.exists(file):
            self.__HdfFileHandleList['Auxily']=self.__HdfOperator.Open(file)

        return

    def SetOrigiRes(self,res):
        """
        设置数据原始分辨率
        :return:
        """
        self.__resORI = res
        print '==========> resORI : ',self.__resORI

    def GetLongitude(self):

        fileHandle = self.__HdfFileHandleList['Longitude']
        datasetName = self.__AuxiliaryDataNamesDict['Longitude']
        lon = fileHandle.select(datasetName).get()

        if (self.__resORI == 500 or self.__resORI == 250):
            RowNum = lon.shape[0]
            ColumnNum = lon.shape[1]
            InputArray = lon
            zoomRate = 1000/self.__resORI
            print "===============开始插值=============="
            temdata = Image.fromarray(InputArray)
            resiziedata = temdata.resize((int(ColumnNum * zoomRate), int(RowNum * zoomRate)), Image.BILINEAR)
            lon = N.array(resiziedata)
            print "===============结束插值=============="

        return lon

    def GetLatitude(self):

        fileHandle = self.__HdfFileHandleList['Latitude']
        datasetName = self.__AuxiliaryDataNamesDict['Latitude']
        lat = fileHandle.select(datasetName).get()

        if (self.__resORI == 500 or self.__resORI == 250):
            RowNum = lat.shape[0]
            ColumnNum = lat.shape[1]
            InputArray = lat
            zoomRate = 1000/self.__resORI
            print "===============开始插值=============="
            temdata = Image.fromarray(InputArray)
            resiziedata = temdata.resize((int(ColumnNum * zoomRate), int(RowNum * zoomRate)), Image.BILINEAR)
            lat = N.array(resiziedata)
            print "===============结束插值=============="

        return lat

    def GetCoefficient(self, filehandle, band):
        m_RefSBCalCoefficientsScales = [0 for i in range(38)]
        m_RefSBCalCoefficientsOffsets = [0 for i in range(38)]
        m_EmissiveRadianceScales = [0 for i in range(38)]
        m_EmissiveRadianceOffsets = [0 for i in range(38)]
        if int(self.__ProjResolution) < 500:
            if int(band[8:]) < 3:
                refcoe250_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_250_RefSB", "reflectance_scales")
                refcoe250_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_250_RefSB", "reflectance_offsets")
                for i in range(0, len(refcoe250_scale)):
                    m_RefSBCalCoefficientsScales[i] = refcoe250_scale[i]
                    m_RefSBCalCoefficientsOffsets[i] = refcoe250_offset[i]
            elif int(band[8:]) < 8:
                refcoe500_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_500_RefSB", "reflectance_scales")
                refcoe500_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_500_RefSB", "reflectance_offsets")
                for i in range(0, len(refcoe500_scale)):
                    m_RefSBCalCoefficientsScales[2 + i] = refcoe500_scale[i]
                    m_RefSBCalCoefficientsOffsets[2 + i] = refcoe500_offset[i]
            else:
                refcoe1000_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_RefSB", "reflectance_scales")
                refcoe1000_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_RefSB", "reflectance_offsets")
                for i in range(0, 6):
                    m_RefSBCalCoefficientsScales[7 + i] = refcoe1000_scale[i]
                    m_RefSBCalCoefficientsOffsets[7 + i] = refcoe1000_offset[i]
                m_RefSBCalCoefficientsScales[13] = refcoe1000_scale[7]
                for i in range(9, 15):
                    m_RefSBCalCoefficientsScales[5 + i] = refcoe1000_scale[i]
                    m_RefSBCalCoefficientsOffsets[5 + i] = refcoe1000_offset[i]
                m_RefSBCalCoefficientsScales[20] = refcoe1000_scale[6]
                m_RefSBCalCoefficientsOffsets[20] = refcoe1000_offset[6]
                m_RefSBCalCoefficientsScales[21] = refcoe1000_scale[8]
                m_RefSBCalCoefficientsOffsets[21] = refcoe1000_offset[8]
                m_EmissiveRadianceScales = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_Emissive",
                                                                             "radiance_scales")
                m_EmissiveRadianceOffsets = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_Emissive",
                                                                              "radiance_offsets")
            return m_RefSBCalCoefficientsScales, m_RefSBCalCoefficientsOffsets, m_EmissiveRadianceScales, m_EmissiveRadianceOffsets
        elif int(self.__ProjResolution) < 1000:
            if int(band[8:]) < 8:
                refcoe250_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_250_Aggr500_RefSB",
                                                                    "reflectance_scales")
                refcoe250_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_250_Aggr500_RefSB",
                                                                     "reflectance_offsets")
                for i in range(0, len(refcoe250_scale)):
                    m_RefSBCalCoefficientsScales[i] = refcoe250_scale[i]
                    m_RefSBCalCoefficientsOffsets[i] = refcoe250_offset[i]
                refcoe500_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_500_RefSB", "reflectance_scales")
                refcoe500_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_500_RefSB", "reflectance_offsets")
                for i in range(0, len(refcoe500_scale)):
                    m_RefSBCalCoefficientsScales[2 + i] = refcoe500_scale[i]
                    m_RefSBCalCoefficientsOffsets[2 + i] = refcoe500_offset[i]
            else:
                refcoe1000_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_RefSB", "reflectance_scales")
                refcoe1000_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_RefSB", "reflectance_offsets")
                for i in range(0, 6):
                    m_RefSBCalCoefficientsScales[7 + i] = refcoe1000_scale[i]
                    m_RefSBCalCoefficientsOffsets[7 + i] = refcoe1000_offset[i]
                m_RefSBCalCoefficientsScales[13] = refcoe1000_scale[7]
                for i in range(9, 15):
                    m_RefSBCalCoefficientsScales[5 + i] = refcoe1000_scale[i]
                    m_RefSBCalCoefficientsOffsets[5 + i] = refcoe1000_offset[i]
                m_RefSBCalCoefficientsScales[20] = refcoe1000_scale[6]
                m_RefSBCalCoefficientsOffsets[20] = refcoe1000_offset[6]
                m_RefSBCalCoefficientsScales[21] = refcoe1000_scale[8]
                m_RefSBCalCoefficientsOffsets[21] = refcoe1000_offset[8]
                m_EmissiveRadianceScales = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_Emissive",
                                                                             "radiance_scales")
                m_EmissiveRadianceOffsets = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_Emissive",
                                                                              "radiance_offsets")
            return m_RefSBCalCoefficientsScales, m_RefSBCalCoefficientsOffsets, m_EmissiveRadianceScales, m_EmissiveRadianceOffsets
        else:
            refcoe250_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_250_Aggr1km_RefSB",
                                                                "reflectance_scales")
            refcoe250_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_250_Aggr1km_RefSB",
                                                                 "reflectance_offsets")
            refcoe500_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_500_Aggr1km_RefSB",
                                                                "reflectance_scales")
            refcoe500_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_500_Aggr1km_RefSB",
                                                                 "reflectance_offsets")
            refcoe1000_scale = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_RefSB", "reflectance_scales")
            refcoe1000_offset = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_RefSB", "reflectance_offsets")
            for i in range(0, len(refcoe250_scale)):
                m_RefSBCalCoefficientsScales[i] = refcoe250_scale[i]
                m_RefSBCalCoefficientsOffsets[i] = refcoe250_offset[i]
            for i in range(0, len(refcoe500_scale)):
                m_RefSBCalCoefficientsScales[2 + i] = refcoe500_scale[i]
                m_RefSBCalCoefficientsOffsets[2 + i] = refcoe500_offset[i]
            for i in range(0, 6):
                m_RefSBCalCoefficientsScales[7 + i] = refcoe1000_scale[i]
                m_RefSBCalCoefficientsOffsets[7 + i] = refcoe1000_offset[i]

            m_RefSBCalCoefficientsScales[13] = refcoe1000_scale[7]

            for i in range(9, 15):
                m_RefSBCalCoefficientsScales[5 + i] = refcoe1000_scale[i]
                m_RefSBCalCoefficientsOffsets[5 + i] = refcoe1000_offset[i]
            m_RefSBCalCoefficientsScales[20] = refcoe1000_scale[6]
            m_RefSBCalCoefficientsOffsets[20] = refcoe1000_offset[6]
            m_RefSBCalCoefficientsScales[21] = refcoe1000_scale[8]
            m_RefSBCalCoefficientsOffsets[21] = refcoe1000_offset[8]

            m_EmissiveRadianceScales = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_Emissive",
                                                                         "radiance_scales")
            m_EmissiveRadianceOffsets = self.__HdfOperator.GetCoefficient(filehandle, "EV_1KM_Emissive",
                                                                          "radiance_offsets")
            return m_RefSBCalCoefficientsScales, m_RefSBCalCoefficientsOffsets, m_EmissiveRadianceScales, m_EmissiveRadianceOffsets

    def DNtoReflectivity(self, bandIndex, DNValue, m_RefSBCalCoefficientsScales, m_RefSBCalCoefficientsOffsets):
        # wTable = numpy.empty((DNValue.size))
        FillValue = 65535
        scale = 1;
        offset = 0;
        # 1,2通道
        if (bandIndex < 19):
            scale = m_RefSBCalCoefficientsScales[bandIndex]
            offset = m_RefSBCalCoefficientsOffsets[bandIndex]
        elif (bandIndex == 25):
            scale = m_RefSBCalCoefficientsScales[19]
            offset = m_RefSBCalCoefficientsOffsets[19]
        elif (bandIndex == 36):
            scale = m_RefSBCalCoefficientsScales[20]
            offset = m_RefSBCalCoefficientsOffsets[20]
        elif (bandIndex == 37):
            scale = m_RefSBCalCoefficientsScales[21]
            offset = m_RefSBCalCoefficientsOffsets[21]
        else:
            return DNValue
        DNValue = DNValue.astype(N.uint16)
        DNOUTrangemask = DNValue > (65535 - 10)
        temp = DNValue[DNOUTrangemask]
        DNValue[DNValue >= 32768] = FillValue
        DNValue[DNValue < 32768] = (DNValue[DNValue < 32768] - offset) * scale * 1000 + 0.5
        DNValue[DNValue < 0] = 0
        DNValue[DNOUTrangemask] = temp
        return DNValue

    def DNtoBrightnessTemperature(self, bandIndex, DNValue, m_EmissiveRadianceScales, m_EmissiveRadianceOffsets):
        # wTable =numpy.empty((DNValue.size))
        FillValue = 65535
        cwn = [2.641775E+03, 2.505277E+03, 2.518028E+03, 2.465428E+03, 2.235815E+03, 2.200346E+03, 0.0, 1.477967E+03,
               1.362737E+03, 1.173190E+03, 1.027715E+03, 9.080884E+02, 8.315399E+02, 7.483394E+02, 7.308963E+02,
               7.188681E+02, 7.045367E+02]
        # Temperature correction slope (no units)
        tcs_buf = [9.993411E-01, 9.998646E-01, 9.998584E-01, 9.998682E-01, 9.998819E-01, 9.998845E-01, 0.0,
                   9.994877E-01, 9.994918E-01, 9.995495E-01, 9.997398E-01, 9.995608E-01, 9.997256E-01, 9.999160E-01,
                   9.999167E-01, 9.999191E-01, 9.999281E-01]
        # Temperature correction intercept (Kelvin)
        tci_buf = [4.770532E-01, 9.262664E-02, 9.757996E-02, 8.929242E-02, 7.310901E-02, 7.060415E-02, 0.0,
                   2.204921E-01, 2.046087E-01, 1.599191E-01, 8.253401E-02, 1.302699E-01, 7.181833E-02, 1.972608E-02,
                   1.913568E-02, 1.817817E-02, 1.583042E-02]

        # Compute brightness temperature

        # Radiance units are
        # Watts per square meter per steradian per micron
        band = bandIndex - 19  # 跟c#的差值1找回来了
        if band < 0 or band == 6 or band == 17 or band == 18:
            return DNValue
        dWaveLength = 1.0e+4 / cwn[band] * 1.0e-6  # unit: meter
        tci = tci_buf[band]
        tcs = tcs_buf[band]
        c = 2.9979246e+8
        h = 6.6260755e-34
        k = 1.380658e-23
        c2 = c * h / k
        c1 = 2.0 * h * c * c
        fRadiance_Scale = 1
        fRadiance_Offsets = 0
        if (band <= 5):
            fRadiance_Scale = m_EmissiveRadianceScales[band]
            fRadiance_Offsets = m_EmissiveRadianceOffsets[band]
        if (band > 6):
            fRadiance_Scale = m_EmissiveRadianceScales[band - 1]
            fRadiance_Offsets = m_EmissiveRadianceOffsets[band - 1]
        print "DNmax", N.max(DNValue[DNValue < 65534])
        print "DNmax", N.min(DNValue[DNValue < 65535])
        DNValue = DNValue.astype(N.uint16)
        DNOUTrangemask = DNValue > 65535
        temp = DNValue[DNOUTrangemask]

        n = math.pow(dWaveLength, 5.0)
        DNValue = DNValue.astype(N.float32)
        DNValue[(DNValue != FillValue)] = ((DNValue[(DNValue != FillValue)] - fRadiance_Offsets) * fRadiance_Scale)
        DNValue[(DNValue <= 0)] = 65535
        rangemask = (DNValue != FillValue) & (DNValue != 0)
        print "DNmax", N.max(DNValue[DNValue < 65534])
        print "DNmax", N.min(DNValue[DNValue < 65535])
        n1 = (c2 / (dWaveLength * N.log(c1 / (n * DNValue[rangemask] * 1.0e6) + 1.0)))  # .astype(numpy.float16)
        print (c2 / (dWaveLength * N.log(c1 / (n * N.max(DNValue[rangemask]) * 1.0e6) + 1.0)))
        print (c2 / (dWaveLength * N.log(c1 / (n * N.min(DNValue[rangemask]) * 1.0e6) + 1.0)))
        print "n1max", N.max(n1)
        print "n1min", N.min(n1)
        n1 = (n1 - tci) / tcs
        DNValue[rangemask] = n1
        DNValue[DNOUTrangemask] = temp
        print "max=", N.max(DNValue[DNValue < 65535])
        print "min=", N.min(DNValue)
        return DNValue * 10

    def GetOBSData(self, band):
        print "--> band wave name : ",band
        self.__bandwaveLength = band
        bandInfo = self.__BandWaveDataNamesDict[int(band[8:])]
        print bandInfo
        bandIndex = int(band[8:])
        datasetName = bandInfo[0]
        datasetIndex = bandInfo[1]

        self.__m_RefSBCalCoefficientsScales,self.__m_RefSBCalCoefficientsOffsets,self.__m_EmissiveRadianceScales,self.__m_EmissiveRadianceOffsets=self.GetCoefficient(self.__HdfFileHandleList['L1'],band)

        ret = None
        if bandInfo != '':
            if self.IsATC==1 and bandIndex <= 16:
                fileHandle = self.__HdfFileHandleList['ATC']
                datasetName = "CorrRefl_"+str(datasetIndex).zfill(2)
                data = fileHandle.select(datasetName).get()
                Slope = 0.1
                data = data*Slope
                data = data.astype(N.uint16)
            else:
                fileHandle = self.__HdfFileHandleList['L1']
                if datasetIndex == -1:
                    data = fileHandle.select(datasetName).get().astype(N.float32)
                else:
                    data = fileHandle.select(datasetName).get()[datasetIndex].astype(N.float32)

                data = self.DNtoReflectivity(bandIndex-1,data,self.__m_RefSBCalCoefficientsScales,self.__m_RefSBCalCoefficientsOffsets)

            ret = self.DNtoBrightnessTemperature(bandIndex-1,data,self.__m_EmissiveRadianceScales,self.__m_EmissiveRadianceOffsets)
            ret = ret.astype(N.uint16)
        print "--> get band data over :!"
        return ret

    def GetAuxiliaryData(self, auxilirayName):

        print ' --> auxiliary name :',auxilirayName

        fileHandle = self.__HdfFileHandleList['Auxily']
        dsname = self.__AuxiliaryDataNamesDict[auxilirayName]

        if dsname:
            auxiData = fileHandle.select(dsname).get()
            if (self.__resORI == 500 or self.__resORI == 250):
                RowNum = auxiData.shape[0]
                ColumnNum = auxiData.shape[1]
                InputArray = auxiData
                zoomRate = 1000 / self.__resORI
                print "===============开始插值=============="
                temdata = Image.fromarray(InputArray)
                resiziedata = temdata.resize((int(ColumnNum * zoomRate), int(RowNum * zoomRate)), Image.BILINEAR)
                auxiData = N.array(resiziedata)

                auxiData[auxiData == -32767] = 65535

                if 'SensorAzimuth' in dsname or 'SolarAzimuth' in dsname:
                    auxiData += 18000

                auxiData = auxiData.astype(N.uint16)
                print "===============结束插值=============="
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

        attrs = dict()

        hour = int(self.GetParameter().TimeFlag[8:10])
        if hour >= 8 and hour <= 20:
            attrs['Orbit Direction'] = 'A'
        else:
            attrs['Orbit Direction'] = 'D'

        infos = self.__HdfFileHandleList['L1'].attributes(full=1)["CoreMetadata.0"][0]
        beginindex = infos.find("DAYNIGHTFLAG")
        endindex = infos[int(beginindex) + 12:].find("DAYNIGHTFLAG") + beginindex

        if infos[int(beginindex) + 12:endindex].find("Day") != -1:
            attrs["Day Or Night Flag"] = "D"
        else:
            attrs["Day Or Night Flag"] = "N"

        return attrs

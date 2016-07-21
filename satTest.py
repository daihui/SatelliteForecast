#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'
#测试文件

import SatForecast as Sat
import time

inputFile='InputFile/visible14-15-0720.Dat'
outputFile='OutputData/SatelliteResult'+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'.txt'
dataForm='dat'

# passSumURL=Sat.satPassSummaryURL(11112)
# satURL,isFlag=Sat.satPassDetailsURL(passSumURL,'2016-7-20-19-18-00',600)
# #print satURL,isFlag
# satellite,isOK=Sat.satDataCollect(11112,satURL,isFlag,5.5)
# #print isOK,satellite.azimuthAngle,satellite.magnitude,satellite.satName
# Sat.dataRecord(satellite,isOK,'OutputData/test.txt')
Sat.satSearch(inputFile,outputFile,dataForm)
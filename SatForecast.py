#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'levitan'
#根据卫星编号在 http://www.heavens-above.com/ 上查询卫星轨道信息并输出文件

from numpy import *
import time
import urllib2
from bs4 import BeautifulSoup

#基本参数设置
baseURL='http://www.heavens-above.com/'
tolerantSecond=15*60    #卫星升起时间容忍误差
minMagnitude=5.5        #卫星筛选星等值
maxSatNum=100           #输入卫星最大颗数
latitude = '32.3260'  # 观测地纬度
longitude = '80.0270'  # 观测地经度
elevation = '5067'  # 观测地海拔，  观测地默认设置阿里观测站(32.3260N,80.0270E,5067)
inputFile = 'InputFile/2016-7-22-input.txt'  # 输入卫星数据，包括编号id以及升起时间
outputFile = 'OutputData/SatelliteResult'+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'.txt'  #输出卫星查询数据
dataForm='txt'  # 输入文件格式


#定义卫星类，属性包括ID，名字，标准时间，北京时间，方位角，星等
class satellite():
    def __init__(self,ID):
        self.id=ID
        self.satName='null'
        self.baseTime=''
        self.altitude= ''
        self.azimuth=''
        self.distance=''
        self.magnitude=1.0
        self.beijingTime=''

#实例化一个卫星
getSatellite=satellite('begin')

#根据ID获得heavens-about数据库关于该卫星的 全部过境 的网页地址
def satPassSummaryURL(ID):
    return "http://www.heavens-above.com/PassSummary.aspx?satid=" + str(
        ID) + "&lat=%s&lng=%s&loc=Ngari&alt=%s&tz=UCT&showall=t" % (latitude, longitude, elevation)


#根据输入卫星的升起时间以容忍度找到目标卫星，获得PassDetailsURL
def satPassDetailsURL(satPassSumURL,passTime,tolerantSecond):
    findFlag=False
    satURL = baseURL
    detailsURL=''
    Day=passTime.split('-')[2]
    passSummaryRequest=urllib2.Request(satPassSumURL)
    passSummaryResponse=urllib2.urlopen(passSummaryRequest, timeout=60)
    passSummary = passSummaryResponse.read()
    summarySoup=BeautifulSoup(passSummary)
    for tr in summarySoup.findAll('tr',attrs={'class':'clickableRow'}):
        if findFlag is False:
            tds = tr.findAll('td')
            satTime = tds[2].text.encode('utf-8')
            satDayTime = passTime.split('-')[0] + passTime.split('-')[1] + passTime.split('-')[2] + satTime
            time1 = time.mktime(time.strptime(satDayTime, "%Y%m%d%H:%M:%S"))
            time2 = time.mktime(time.strptime(passTime, "%Y-%m-%d-%H-%M-%S"))
            detT = abs(int(time1) - int(time2))
            # print detT
            day = tds[0].text.encode("utf-8").split(' ')[0]
            detailsURL = tds[0].find('a').attrs['href']
            if Day == day and detT < tolerantSecond:
                satURL = satURL + detailsURL
                findFlag = True
                break
    return satURL, findFlag

#根据找到的卫星爬取卫星数据，存入satellite实例
def satDataCollect(id,satURL,isFind,minMagnitude):
    isOK=False
    if isFind:
        try:
            # print satURL
            passDetailsRequest = urllib2.Request(satURL)
            passDetailsResponse = urllib2.urlopen(passDetailsRequest, timeout=60)
            passDetails = passDetailsResponse.read()
            detailsSoup = BeautifulSoup(passDetails)
            head = detailsSoup.find('head')
            name = head.find('title').text.encode('utf-8').split('-')[0].strip()
            table = detailsSoup.find('table', attrs={'standardTable'})
            trs = table.findAll('tr')
            tr = trs[3]
            tds = tr.findAll('td')
            if tds[0].text.encode('utf-8').strip() != 'Maximum altitude':
                tr = trs[4]
                tds = tr.findAll('td')
            if tds[5].text.encode('utf-8').strip() != '-':
                print tds[5].text.encode('utf-8').strip()
                if float(tds[5].text.encode('utf-8').strip()) <= minMagnitude:
                    getSatellite.altitude = tds[2].text.encode('utf-8').split(' ')[0].strip()
                    getSatellite.magnitude = float(tds[5].text.encode('utf-8'))
                    getSatellite.azimuth = tds[3].text.encode('utf-8').split(' ')[0].strip()
                    getSatellite.distance = tds[4].text.encode('utf-8')
                    getSatellite.satName = name
                    isOK = True
                else:
                    print 'Magnitude is bigger than %s' % minMagnitude
            else:
                print 'Satellite %s Magnitude information is - (not clear!)' % getSatellite.id
        except Exception, e:
            print 'Satellite %s internet timeout ! please check this URL below：' % getSatellite.id
            print satURL
    else:
        print 'Can\'t find the Satellite id %s around time %s !, Please check!' % (
        getSatellite.id, getSatellite.baseTime)
    return getSatellite,isOK

#将符合要求的卫星数据写入文件
def dataRecord(satellite,isOK,outputFile):
    if isOK:
        resultFile=open(outputFile,'a')
        baseTime=satellite.baseTime
        baseTimeSed=time.mktime(time.strptime(baseTime,"%Y-%m-%d-%H-%M-%S"))
        beijingTimeSed=baseTimeSed+8*60*60.0
        baseTimeStr=time.strftime('%H:%M',time.localtime(baseTimeSed))
        beijingTimeStr=time.strftime('%H:%M',time.localtime(beijingTimeSed))
        resultFile.write("%s\t%s\t%s\t%s\t%s\t%.1f\t%s\t%s\n"%(satellite.satName,satellite.id,baseTimeStr,satellite.altitude,satellite.azimuth,satellite.magnitude,satellite.distance,beijingTimeStr))
        resultFile.close()

#读取txt格式的输入卫星数据
# 文本行格式必须为 id\t time \t\n
def txtReadToList(inputFile):
    dataInput=open(inputFile,'r')
    satList=zeros([len(dataInput.readlines()),2])
    dataInput.close()
    dataInput=open(inputFile,'r')
    Day=time.strftime('%Y-%m-%d',time.localtime(int(time.time())))
    #print Day
    i=0
    for line in dataInput.readlines():
        satList[i][0]=line.split('\t')[0]
        tempTime= str(line.split('\t')[1])
        tempTime=tempTime.split('\n')[0]
        dayTime=time.strptime(tempTime,'%H:%M')
        dayTime=time.strftime('-%H-%M-%S',dayTime)
        dayTime=Day+dayTime
        startTime= time.mktime(time.strptime(dayTime,"%Y-%m-%d-%H-%M-%S"))
        satList[i][1]=startTime
        i+=1
    dataInput.close()
    return satList

#读取dat格式的输入卫星数据
# 文本行格式必须为 id  Ymd  HMS000
def datReadToList(inputFile):
    satList=zeros([maxSatNum,2])
    dataInput=open(inputFile,'r')
    i=0
    idFlag=0
    for line in dataInput.readlines():
        if idFlag==int(line.split(' ')[0]):
            continue
        else:
            satList[i][0]=line.split()[0]
            tempTime=line.split()[1]+line.split()[2][0:5]
            startTime= time.mktime(time.strptime(tempTime,"%Y%m%d%H%M%S"))
            satList[i][1]=startTime
            idFlag=int(line.split()[0])
            #print satList[i]
            i+=1
    dataInput.close()
    return satList

#卫星数据查询函数
def satSearch(inputFile,outputFile,dataForm):
    if dataForm=='txt':
        satList=txtReadToList(inputFile)
    elif dataForm=='dat':
        satList=datReadToList(inputFile)
    else:
        print 'The input data form is not support !!! try .txt or .dat file!'

    satNum=int(len(satList))
    outFile=open(outputFile,'a')
    outFile.write('Satellite\tID\tTime(UTC+00:00)\tAltitude(高度)\tAzimuth(方位角)\tMagnitude(星等)\tDistance(km)\tTime(UTC+08:00)\n')
    outFile.close()
    print'Satellite MaxNum:', satNum
    for i in range(satNum):
        print str(i+1) + '\'th satellite:'
        if int(satList[i][0])==0:
            continue
        getSatellite.id=str(int(satList[i][0]))
        baseTime=time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(satList[i][1]))
        getSatellite.baseTime=baseTime
        PassSummaryURL=satPassSummaryURL(getSatellite.id)
        satURL,isFind=satPassDetailsURL(PassSummaryURL,getSatellite.baseTime,tolerantSecond)
        #print satURL,isFind
        Satellite,isOK=satDataCollect(getSatellite.id,satURL,isFind,minMagnitude)
        if isOK:
            dataRecord(Satellite,isOK,outputFile)
            print 'The satellite: ' + getSatellite.id + '\t' + 'OK ' + str(getSatellite.magnitude)


if __name__ == "__main__":
    satSearch(inputFile,outputFile,dataForm)
    print 'finished!'
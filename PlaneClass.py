#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from FlightRecovery.EnvironmentData import EnvironmentData as ED

class Plane(object):
    """飞机类"""
    def __init__(self,id,style,startTime,endTime,startAirport,seatNum):
        self.style=style
        self.id=id
        self.startTime=startTime
        self.endTime=endTime
        self.startAirport=startAirport
        self.seatNum=seatNum
        #由于飞机的起飞检修时间不一定是整点时刻，所以Time用以储存活动时段，status储存对应序列活动时段的活动内容
        self.Time=[]
        self.status=[]
        st=ED['STARTTIME']
        et=ED['ENDTIME']
        if(st!=startTime):
            t=[st,startTime]
            self.Time.append(t)
            self.status.append('stop')
        t=[startTime,endTime]
        self.Time.append(t)
        self.status.append('waiting')
        t=[endTime,et]
        self.Time.append(t)
        self.status.append('stop')

    def isWaiting(self,st,et):
        index=len(self.Time)-2
        if(self.status[index]!='waiting'):
            return False
        if((self.Time[index][0]<=st)and(self.Time[index][1]>=et)):
            return True
        else:
            return False

    def addTask(self,st,et):
        ct=ED['CHECKTIME']
        isWaiting=self.isWaiting(st,et)
        if(not isWaiting):
            return False
        index=len(self.Time)-2
        self.Time[index][1]=st
        t=[st,et]
        self.Time.insert(index+1,t)
        self.status.insert(index+1,'flying')
        if(et!=self.Time[index+2][0]):
            if(et+ct>=self.Time[index+2][0]):
                t=[et,self.Time[index+2][0]]
                self.Time.insert(index+2,t)
                self.status.insert(index+2,'checking')
            else:
                t=[et,et+ct]
                self.Time.insert(index+2,t)
                self.status.insert(index+2,'checking')
                t=[et+ct,self.Time[index+3][0]]
                self.Time.insert(index+3,t)
                self.status.insert(index+3,'waiting')
        return True


    #返回飞机可执行任务时段的起始时间
    def getStartTimeOfWaiting(self):
        index=len(self.Time)-2
        return self.Time[index][0]



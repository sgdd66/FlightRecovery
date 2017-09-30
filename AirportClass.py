#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from FlightRecovery.EnvironmentData import EnvironmentData as ED

class Airport(object):
    '''机场类'''

    def __init__(self,id):
        self.id=id
        st=ED['STARTTIME']
        et=ED['ENDTIME']
        it=ED['INTERVAL']
        num=int((et-st)/it)
        self.hangar=[]
        self.numOff=np.zeros(num)
        self.numLand=np.zeros(num)
        self.maxOff = np.zeros(num)+500
        self.maxLand = np.zeros(num)+500
        for i in range(0,num):
            hangar = []
            self.hangar.append(hangar)



    #飞机着陆
    def PlaneLand(self,plane,time):

        st=ED['STARTTIME']
        it=ED['INTERVAL']
        index=(time-st)//it
        if(self.numLand[index]<self.maxLand[index]):
            self.numLand[index]+=1

        else:
            return False
        for i in range(index,len(self.hangar)):
            self.hangar[i].append(plane)
        return True

    #飞机起飞
    def PlaneOff(self,plane,time):
        st=ED['STARTTIME']
        it=ED['INTERVAL']
        index=(time-st)//it
        if(plane not in self.hangar[index]):
            return False
        else:
            if(self.numOff[index]<self.maxOff[index]):
                self.numOff[index]+=1
                for i in range(index, len(self.hangar)):
                    if(plane not in self.hangar[i]):
                        print("time:{0},plane:{1},airport:{2},")
                    self.hangar[i].remove(plane)
                return True
            else:
                return False

    #是否可以起飞
    def canOff(self,flight):
        time=flight.realStartTime
        st=ED['STARTTIME']
        it=ED['INTERVAL']
        index=(time-st)//it
        # if(self.id=='OVS' and index==195):
        #     print('stop')
        plane=flight.plane
        if(plane not in self.hangar[index]):
            if(not flight.CanExchange):
                return False
            else:
                isOK=self.exchangePlane(flight)
                if(not isOK):
                    return False
        else:
            flight.realPlane=plane


        if(self.numOff[index]<self.maxOff[index]):
            return True
        else:
            return False

    #是否可以降落
    def canLand(self,flight):
        time=flight.realArriveTime
        st = ED['STARTTIME']
        it = ED['INTERVAL']
        index = (time - st) // it
        if (self.numLand[index] < self.maxLand[index]):
            return True
        else:
            return False

    #置换航班飞机
    def exchangePlane(self,flight):
        fst=flight.realStartTime
        fat=flight.realArriveTime
        st=ED['STARTTIME']
        it=ED['INTERVAL']
        index=(fst-st)//it
        planes=self.hangar[index].copy()
        for plane in planes:
            if(not plane.isWaiting(fst,fat)):
                planes.remove(plane)
        if(len(planes)==0):
            return False

        cost=[]
        for plane in planes:
            cost.append(self.exchangeCost(flight,plane))
        cost=np.array(cost)
        index=np.where(cost==min(cost))
        flight.realPlane=planes[index[0][0]]
        return True

    #计算置换飞机的成本
    def exchangeCost(self,flight,plane):
        question=ED['QUESTION']

        if(question==1):
            delayTime=(plane.getStartTimeOfWaiting()-flight.startTime)
            return delayTime
        elif(question==2):
            delayTime1=(plane.getStartTimeOfWaiting()-flight.startTime)
            if(flight.plane.style==plane.style):
                delayTime2=0
            else:
                delayTime2=30*60
            return delayTime1+delayTime2
        elif(question==3):
            delayTime1 = (plane.getStartTimeOfWaiting() - flight.startTime) * plane.seatNum
            if (flight.plane.style == plane.style):
                delayTime2 = 0
            else:
                delayTime2 = 30 * 60 * plane.seatNum
            seatDiff=flight.plane.seatNum-plane.seatNum
            if(seatDiff>0):
                delayTime3=2*60*60*seatDiff
            else:
                delayTime3=0
            return delayTime1+delayTime2+delayTime3
        elif(question==4):
            delayTime1 = (plane.getStartTimeOfWaiting() - flight.startTime) * flight.population
            seatDiff = flight.population - plane.seatNum
            if (seatDiff > 0):
                delayTime2 = 24 * 60 * 60 * seatDiff
            else:
                delayTime2 = 0
            return delayTime1 + delayTime2

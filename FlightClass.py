#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""航班类"""

import numpy as np
from FlightRecovery.PlaneClass import Plane
from FlightRecovery.EnvironmentData import EnvironmentData as ED

class Flight(object):
    """航班类"""
    def __init__(self,id,startTime,arriveTime,startAirport,arriveAirport,plane):
        self.id=id
        self.startTime=startTime
        self.arriveTime=arriveTime
        self.realArriveTime=arriveTime
        self.realStartTime=startTime
        self.flyTime=arriveTime-startTime
        self.startAirport=startAirport
        self.arriveAirport=arriveAirport
        self.plane=plane
        self.realPlane=plane
        self.cabin=[]
        self.population=0
        self.status='waiting'
        self.CanExchange=True

    def addPassenger(self,passenger):
        population=self.population+passenger.population
        if(population<self.plane.seatNum):
            self.population=population
            self.cabin.append(passenger)
            return True
        else:
            return False
    #航班完成
    def finish(self):
        self.status='finished'
        population=self.population
        seat=self.realPlane.seatNum
        if(seat<population):
            self.cabin.sort(reverse=True)
            diff=population-seat
            for i in range(0,len(self.cabin)):
                passenger=self.cabin.pop()
                passenger.status='refuse'
                diff-=passenger.population
                if diff<=0:
                    break

        for passenger in self.cabin:
            passenger.status='finished'

    def __cmp__(self, other):
        if self.__eq__(other):
            return 0
        elif self.__lt__(other):
            return -1
        elif self.__gt__(other):
            return 1



    def __gt__(self, other):
        if(self.realStartTime>other.realStartTime):
            return True
        elif(self.realStartTime==other.realStartTime):
            if (self.flyTime > other.flyTime):
                return True
            elif(self.flyTime==other.flyTime):
                if self.id>other.id:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def __lt__(self, other):
        if(self.realStartTime<other.realStartTime):
            return True
        elif(self.realStartTime==other.realStartTime):
            if (self.flyTime < other.flyTime):
                return True
            elif self.flyTime==other.flyTime:
                if self.id<other.id:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    def __eq__(self, other):
        if(other==None):
            return False
        if(id(self)==id(other)):
            return True
        elif(self.realStartTime==other.realStartTime and self.flyTime == other.flyTime and self.id==other.id):
            return True

    #航班延误处理，返回TRUE处理成功，返回FALSE代表航班取消
    def delay(self,num=1):
        if(num==0):
            return True
        it=ED['INTERVAL']
        maxDelayTime=ED['MAXDELAYTIME']
        if(self.startTime-self.realStartTime==0):
            index=self.startTime//it+num
            self.realStartTime=index*it
            self.realArriveTime=self.realStartTime+self.flyTime
            return True
        else:
            if(self.realStartTime-self.startTime+it*num>maxDelayTime):
                self.status='cancel'
                # print("flight id:{0} cancel".format(self.id))
                return False
            else:
                self.realStartTime+=it*num
                self.realArriveTime+=it*num
                return True



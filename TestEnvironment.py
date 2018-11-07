#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""本程序用于对航班恢复算法的结果提供检验模型"""

import numpy as np
import matplotlib.pyplot as plt


from FlightRecovery.EnvironmentData import EnvironmentData as ED
from FlightRecovery.AirportClass import Airport
from FlightRecovery.PlaneClass import Plane
from FlightRecovery.FlightClass import Flight
from FlightRecovery.PassengerClass import Passenger




class Environment(object):
    """测试环境"""

    def __init__(self):
        #构建所有的机场对象
        File=open("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\Airport.txt",'r+')
        lines=File.readlines()
        Airports=[]
        for line in lines:
            item=line.strip()
            airport=Airport(item)
            Airports.append(airport)
        self.Airports=Airports

        airport=self.getAirport('OVS')
        airport.maxOff[:]=10
        airport.maxLand[:]=10
        airport.maxLand[0]=500
        closeST=1461348000
        closeET=1461358800
        st=ED['STARTTIME']
        it=ED['INTERVAL']
        sIndex=(closeST-st)//it
        eIndex=(closeET-st)//it
        if((closeET-st)%it!=0):
            eIndex+=1
            eIndex=int(eIndex)
        airport.maxOff[sIndex:eIndex]=0
        airport.maxLand[sIndex:eIndex]=0



        #构建所有的飞机类
        question=ED['QUESTION']
        if(question==1):
            File = open("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\Aircraft_1.txt", 'r+')
        else:
            File = open("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\Aircraft.txt", 'r+')
        lines = File.readlines()
        Planes = []
        for line in lines:
            items = line.strip().split('\t')
            startAirport=self.getAirport(items[4])
            plane = Plane(items[0],items[1],int(items[2]),int(items[3]),startAirport,int(items[5]))
            Planes.append(plane)
        self.Planes = Planes

        #构建所有航班类
        if(question==1):
            file = open("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\Schedules_1.txt", 'r+')
        else:
            file = open("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\Schedules.txt", 'r+')
        lines=file.readlines()
        Flights=[]
        for line in lines:
            items=line.strip().split('\t')
            plane=self.getPlane(items[6])
            startAirport=self.getAirport(items[3])
            arriveAirport=self.getAirport(items[4])
            flight=Flight(int(items[0]),int(items[1]),int(items[2]),startAirport,arriveAirport,plane)
            Flights.append(flight)
        self.Flights=Flights
        self.Flights.sort()

        # self.error=[]
        #构建所有的旅客类
        file = open("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\PaxinfoAfterCheck.txt", 'r+')
        lines=file.readlines()
        self.passengerID=set()
        Passengers=[]
        for line in lines:
            items=line.strip().split('\t')
            flight=self.getFlight(int(items[1]))
            # if(flight==None):
            #     self.error.append(line)
            passenger=Passenger(items[0],flight,int(items[2]))
            Passengers.append(passenger)
            self.passengerID.add(items[0])
        self.Passengers=Passengers

        # print("Airport quantity",len(self.Airports))
        # print("plane quantity",len(self.Planes))
        # print("flight quantity",len(self.Flights))

        self.PlaneToAirport()
        self.PassengerToFlight()

        # self.ExecuteFlight()
        # self.outputFile()



        # error=self.error
        # File = open("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\error.txt", 'w+')
        # for lines in error:
        #     File.writelines(lines)

    #将飞机运入机场机库
    def PlaneToAirport(self):
        st=ED['STARTTIME']
        planes=self.Planes
        airports=self.Airports
        for plane in planes:
            plane.startAirport.PlaneLand(plane,st)

    #将乘客送入机舱，注意机舱属性附属于航班，而不是飞机
    def PassengerToFlight(self):
        passengers=self.Passengers
        for passenger in passengers:
            flight=passenger.flight
            # if(flight==None):
            #     continue
            success=True
            if(flight==None):
                passenger.status="refuse"
            else:
                success=flight.addPassenger(passenger)
            if(not success):
                self.ChangeTicket(passenger)

    #执行航班任务
    def ExecuteFlight(self):
        Flights=self.Flights.copy()
        Flights.sort(reverse=True)
        while(len(Flights)!=0):

            flight=Flights.pop()
            if(flight.id=='174777634'):
                st=ED['STARTTIME']
                it=ED['INTERVAL']
                if((flight.realStartTime-st)//it==273):
                    print('stop')
            ready=flight.startAirport.canOff(flight)
            if(not ready):
                if(flight.delay()):
                    Flights.append(flight)
                    Flights.sort(reverse=True)
                    continue
                else:
                    continue
            ready=flight.arriveAirport.canLand(flight)
            if(not ready):
                if (flight.delay()):
                    Flights.append(flight)
                    Flights.sort(reverse=True)
                    continue
                else:
                    continue
            ready=flight.realPlane.isWaiting(flight.realStartTime,flight.realArriveTime)
            if(not ready):
                if(flight.CanExchange):
                    isOK=flight.startAirport.exchangePlane(flight)
                    if(not isOK):
                        if (flight.delay()):
                            Flights.append(flight)
                            Flights.sort(reverse=True)
                            continue
                        else:
                            continue
                else:
                    if (flight.delay()):
                        Flights.append(flight)
                        Flights.sort(reverse=True)
                        continue
                    else:
                        continue

            flight.realPlane.addTask(flight.realStartTime,flight.realArriveTime)
            flight.startAirport.PlaneOff(flight.realPlane,flight.realStartTime)
            flight.arriveAirport.PlaneLand(flight.realPlane,flight.realArriveTime)
            flight.finish()

    #机票改签
    def ChangeTicket(self,passenger):
        print('passenger id:{0},flight id:{1} is changing ticket'.format(passenger.id,passenger.flight.id))
        st=passenger.flight.startTime
        sA=passenger.flight.startAirport
        aA=passenger.flight.arriveAirport
        flights=self.Flights
        option=[]
        for flight in flights:
            if((flight.startAirport==sA)and(flight.arriveAirport==aA)and(flight.startTime>st)):
                if((flight.population+passenger.population)<flight.plane.population):
                    option.append(flight)
        if(len(option)==0):
            passenger.status='refuse'
            # print("change ticket failed")
            return False

        aim=option[0]
        waitTime=option.startTime-st
        for op in option:
            if((op.startTime-st)<waitTime):
                aim=op
        passenger.flight=aim
        aim.addPassenger(passenger)
        # print("change ticket succeed")
        return True

    #通过id获得相应飞机
    def getPlane(self,id):
        planes=self.Planes
        for plane in planes:
            if(id==plane.id):
                return plane
        return None

    # 通过id获得相应机场
    def getAirport(self,id):
        airports=self.Airports
        for airport in airports:
            if(id==airport.id):
                return airport
        return None

    # 通过id获得相应航班
    def getFlight(self,id):
        flights=self.Flights
        for flight in flights:
            if(id==flight.id):
                return flight
        return None

    #输出文件
    def outputFile(self):
        st=ED['STARTTIME']
        it=ED['INTERVAL']
        file=open("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\outcome.txt",'w+')
        self.Flights.sort()
        for flight in self.Flights:
            str='{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\r\n'.format(
                flight.id,
                flight.startTime,
                flight.realStartTime,
                flight.arriveTime,
                flight.realArriveTime,
                # (flight.startTime - st) // it,
                # (flight.realStartTime - st) // it,
                # (flight.arriveTime - st) // it,
                # (flight.realArriveTime - st) // it,
                flight.startAirport.id,
                flight.arriveAirport.id,
                flight.plane.style,
                flight.realPlane.style,
                flight.plane.id,
                flight.realPlane.id,
                flight.realStartTime-flight.startTime,
                flight.status
            )
            file.writelines(str)
        file.close()

        # airport=self.getAirport('PXM')
        # data=np.zeros(len(airport.hangar))
        # hangar=airport.hangar
        # for i in range(0,len(airport.hangar)):
        #     data[i]=len(airport.hangar[i])
        # np.savetxt("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\hangarNum.txt", data,
        #            fmt='%d\t')

        # np.savetxt("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\land.txt",airport.numLand,fmt='%d\t')
        # np.savetxt("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\off.txt",airport.numOff,fmt='%d\t')
        #
        # num=0
        # for flight in self.Flights:
        #     if(flight.startAirport==airport or flight.arriveAirport==airport):
        #         num+=1
        # print(num)

    def CalculateCost(self):
        question=ED['QUESTION']
        cancelCost=ED['CANCELCOST']
        costInAll=0
        if question==1:
            for flight in self.Flights:
                cost=0
                if flight.status=='cancel':
                    cost+=cancelCost
                else:
                    cost+=flight.realStartTime-flight.startTime
                costInAll+=cost
        elif question==2:
            for flight in self.Flights:
                cost=0
                if flight.status=='cancel':
                    cost+=cancelCost
                else:
                    cost+=flight.realStartTime-flight.startTime
                    if(flight.plane.style!=flight.realPlane.style):
                        cost+=30*60
                costInAll+=cost
        elif question==3:
            for flight in self.Flights:
                cost=0
                if flight.status=='cancel':
                    cost+=cancelCost*flight.plane.seatNum
                else:
                    cost+=(flight.realStartTime-flight.startTime)*flight.realPlane.seatNum
                    if (flight.plane.style!=flight.realPlane.style):
                        cost+=30*60*flight.realPlane.seatNum
                        if(flight.plane.seatNum>flight.realPlane.seatNum):
                            diff=flight.plane.seatNum-flight.realPlane.seatNum
                            cost+=2*60*60*diff
                costInAll+=cost
        elif question==4:

            for id in self.passengerID:
                cost=0
                list=[]
                flights = []
                for passenger in self.Passengers:
                    if passenger.id==id:
                        list.append(passenger)
                        flights.append(passenger.flight)
                flights.sort()
                isOK=True
                for i in range(0,len(flights)-1):
                    if flights[i].status=='cancel':
                        cost+=24*60*60*list[0].population
                        isOK=False
                        break
                    elif(flights[i+1].realStartTime-flights[i].realArriveTime<45*60):
                        cost+=24*60*60*list[0].population
                        isOK=False
                        break
                if(isOK):
                    if flights[len(flights)-1].status=='cancel':
                        cost += 24 * 60 * 60 * list[0].population
                        isOK = False
                if(isOK):
                    flight=flights[len(flights)-1]
                    cost+= (flight.realStartTime-flight.startTime)* list[0].population
                costInAll+=cost
        return costInAll

    def getCost(self,gene):
        self.changeDelayTime(gene)
        self.ExecuteFlight()
        costInAll=self.CalculateCost()
        self.recover()
        return costInAll

    #计算完成之后恢复现场
    def recover(self):
        for passenger in self.Passengers:
            passenger.status='waiting'
        for flight in self.Flights:
            flight.realStartTime=flight.startTime
            flight.realArriveTime=flight.arriveTime
            flight.realPlane=flight.plane
            flight.cabin=[]
            flight.population=0
            flight.status='waiting'
            flight.CanExchange=True
        self.Flights.sort()

        st = ED['STARTTIME']
        et = ED['ENDTIME']
        it = ED['INTERVAL']
        num = int((et - st) / it)
        for airport in self.Airports:
            airport.hangar = []
            airport.numOff = np.zeros(num)
            airport.numLand = np.zeros(num)
            for i in range(0, num):
                hangar = []
                airport.hangar.append(hangar)

        for plane in self.Planes:
            plane.Time = []
            plane.status = []
            if (st != plane.startTime):
                t = [st, plane.startTime]
                plane.Time.append(t)
                plane.status.append('stop')
            t = [plane.startTime, plane.endTime]
            plane.Time.append(t)
            plane.status.append('waiting')
            t = [plane.endTime, et]
            plane.Time.append(t)
            plane.status.append('stop')
        self.PlaneToAirport()
        self.PassengerToFlight()

    def changeDelayTime(self,gene):
        for i in range(0,len(gene)):
            g=int(gene[i])
            delayNum=g&31
            self.Flights[i].delay(delayNum)
            canExchange=g&32
            if(canExchange):
                self.Flights[i].CanExchange=True
            else:
                self.Flights[i].CanExchange=False



if __name__=="__main__":
    test=Environment()
    # test.ExecuteFlight()
    # test.outputFile()
    # list=[]
    # for flight in test.Flights:
    #     list.append(flight.realStartTime-flight.startTime)
    # a=np.array(list)
    # print(np.sum(a)*10)
    data=np.loadtxt("E:/BestGene.txt")
    proportion=np.loadtxt("E:/BestGeneProportion.txt")
    row=data.shape[0]
    delaytime=np.zeros(row)
    for i in range(row):
        delaytime[i]=test.getCost(data[i,:])
    np.savetxt("E:/delaytime.txt", delaytime, fmt='%d\t')


    # bestIndex=np.where(delaytime==min(delaytime))
    # bestIndex=bestIndex[0][0]
    # test.changeDelayTime(data[bestIndex,:])
    # test.ExecuteFlight()
    # test.outputFile()
    # print(delaytime[bestIndex])

    # delaytime=np.loadtxt("E:/delaytime.txt")

    x=np.arange(1,row+1,1)
    plt.plot(x,delaytime)
    plt.xlabel("Generation")
    plt.ylabel("Delay Time")
    plt.show()

    plt.plot(x,proportion)
    plt.xlabel("Generation")
    plt.ylabel("Proportion")
    plt.show()



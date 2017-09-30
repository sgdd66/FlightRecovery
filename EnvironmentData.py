#!/usr/bin/env python
# -*- coding: utf-8 -*-
EnvironmentData={
    'STARTTIME':1461241800,
    'ENDTIME':1461510000,
    'INTERVAL':600,
    'CHECKTIME':2700,       #飞机飞行后的检修时间
    'CANCELCOST':48000,     #飞机的取消成本
    'MAXDELAYTIME': 18000,
    'QUESTION':3,           #当前求解的问题
    'ABERRANCERATE':0.2,   #变异率
    'EXCHANGERATE':0.8,      #交换率
    'MAXCOST':100000000000,           #计算过程中所能出现的最大延误成本
    'MAXPROPORTION':0.6,    #最优个体在群体中的最大占比
    'BESTPROTECTRATE':0.05  #为最优个体提供保护的程度
}
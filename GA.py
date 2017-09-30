#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""为航班恢复问题搭建遗传算法"""

from FlightRecovery.EnvironmentData import EnvironmentData as ED
from FlightRecovery.TestEnvironment import Environment
import numpy as np

class Individual(object):
    """个体类，包含基因信息"""
    def __init__(self,flightNum):
        """生成个体"""

        self.gene=np.random.randint(32,36,flightNum)
        self.check()
        self.fitness=0

    #检查个体的基因在生成或者变化后是否有效，若有错误编码，进行变异调整为正常值
    def check(self):
        gene=self.gene
        for i in range(0,len(gene)):
            while(gene[i]==63 or gene[i]==31):
                gene[i]=np.random.randint(0,64)

    #变异的基本单位是片段
    def aberrance(self):
        rate=ED['ABERRANCERATE']
        num=len(self.gene)*rate
        num=int(num)
        if(num==0):
            num=int(1)
        for i in range(0,num):
            index=np.random.randint(0,len(self.gene))
            rand1=np.random.randint(0,3)
            rand2=np.random.normal()
            delayTime=self.gene[index]&31
            if(rand2>0):
                delayTime+=1
            elif delayTime>0:
                delayTime-=1
            if(rand1!=0):
                delayTime+=32

            self.gene[index]=delayTime
        self.check()

    #交换的基本单位是片段,本函数用于给出待交换的基因片段
    def exchangeFragment_out(self,exBit):
        fragment=[]
        for index in exBit:
            index=int(index)
            fragment.append(self.gene[index])
        return fragment

    #交换的基本单位是片段,本函数用于修改待交换的基因片段
    def exchangeFragment_in(self,exBit,fragment):
        for index,chip in zip(exBit,fragment):
            index=int(index)
            self.gene[index]=chip



    #求个体的适应度
    def getFitness(self,TestEnvironment):
        maxCost=ED['MAXCOST']
        self.fitness=maxCost-TestEnvironment.getCost(self.gene)
        if(self.fitness<0):
            self.fitness=0

    def __cmp__(self, other):
        if(self.fitness>other.fitness):
            return 1
        elif(self.fitness<other.fitness):
            return -1
        elif(self.fitness==other.fitness):
            return 0

    def __gt__(self, other):
        if(self.fitness>other.fitness):
            return True
        else:
            return False

    def __lt__(self, other):
        if(self.fitness<other.fitness):
            return True
        else:
            return False

    def __eq__(self, other):
        if(self.fitness==other.fitness):
            return True
        else:
            return False

    def __deepcopy__(self, memodict={}):
        new=Individual(len(self.gene))
        for i in range(0,len(self.gene)):
            new.gene[i]=self.gene[i]
        return new


class GA(object):

    def __init__(self,TestEnvironment,population):
        self.testEnvironment=TestEnvironment
        flightNum=len(TestEnvironment.Flights)
        self.individual=[]
        for i in range(0,population):
            ind=Individual(flightNum)
            self.individual.append(ind)
        for i in range(len(self.individual[0].gene)):
            self.individual[0].gene[i]=32
        self.bestProportion=0
        self.generationNum=0
        self.maxGeneration=0
        self.maxProportion=ED['MAXPROPORTION']
        self.data=[]
        self.proportion=[]

    #获取最优群体在种群中的占比
    def getBestProportion(self):
        self.individual.sort(reverse=True)
        bestOutcome=self.individual[0].fitness
        bestNum=0
        for ind in self.individual:
            if ind.fitness==bestOutcome:
                bestNum+=1
            else:
                break
        self.bestProportion=bestNum/len(self.individual)
        self.proportion.append(self.bestProportion)


    def OutputFile(self):
        bestGene=np.array(self.data)
        np.savetxt("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\BestGene.txt",bestGene,
                   fmt='%d\t',
                   newline='\r\n')
        p=np.array(self.proportion)
        np.savetxt("C:\\Users\\Administrator\\Documents\\Python Project\\FlightRecovery\\BestGeneProportion.txt",p,
                   fmt='%.5f\t',
                   newline='\r\n')



    def evolution(self,generationNum):
        self.maxGeneration=generationNum

        while(True):
            #计算适应度
            for ind in self.individual:
                ind.getFitness(self.testEnvironment)

            self.getBestProportion()
            self.generationNum+=1

            maxCost = ED['MAXCOST']
            print("当前进化代数：{0}，延误成本最小值：{1}，最优值占比{2}".format(
                self.generationNum,
                maxCost - self.individual[0].fitness,
                self.bestProportion
            ))
            d=np.zeros(len(self.individual[0].gene))
            d[:]=self.individual[0].gene[:]
            self.data.append(d)
            if(self.generationNum>self.maxGeneration or self.bestProportion>self.maxProportion):
                break
            # if(self.generationNum==15):
            #     for i in range(len(self.individual[0].gene)):
            #         self.individual[0].gene[i]=32
            self.OutputFile()

            #选择
            nextIndividual = []
            rate=ED['BESTPROTECTRATE']
            bestNum=int(len(self.individual)*rate)+1
            if(bestNum<2):
                bestNum=2
            for i in range(bestNum):
                ind = self.individual[0].__deepcopy__()
                nextIndividual.append(ind)
            rands = np.random.normal(size=int(len(self.individual)-bestNum))
            rands = np.abs(rands)
            bin = np.linspace(0, 3, len(self.individual)-1)

            for rand in rands:
                index=0
                for b in bin:
                    if(rand>b):
                        index+=1
                    else:
                        break
                if index==0:
                    print('stop')
                ind=self.individual[index].__deepcopy__()
                nextIndividual.append(ind)
            self.individual=nextIndividual

            #交换操作
            rate=ED['EXCHANGERATE']
            exIndNum=rate*len(self.individual)
            exGeNum=rate*len(self.individual[0].gene)

            if(exIndNum%2<1):
                exIndNum=int(exIndNum)
            else:
                exIndNum=int(exIndNum+1)
            if(exIndNum<2):
                exIndNum=int(2)

            if(exGeNum<1):
                exGeNum=int(1)
            else:
                exGeNum=int(exGeNum)

            rands=np.random.randint(0,len(self.individual),exIndNum)
            for i in range(0,int(exIndNum/2)):
                i1=rands[i]
                i2=rands[int(i+exIndNum/2)]
                exbit=np.random.randint(0,len(self.individual[0].gene),exGeNum)
                fragmentA=self.individual[i1].exchangeFragment_out(exbit)
                fragmentB=self.individual[i2].exchangeFragment_out(exbit)
                self.individual[i1].exchangeFragment_in(exbit,fragmentB)
                self.individual[i2].exchangeFragment_in(exbit,fragmentA)

            #变异操作
            rate=ED['ABERRANCERATE']
            num=rate*len(self.individual)
            if(num>1):
                num=int(num)
            else:
                num=int(1)
            rands=np.random.randint(0,len(self.individual),num)
            for rand in rands:
                self.individual[rand].aberrance()
        self.OutputFile()

if __name__=='__main__':
    te=Environment()
    test=GA(te,100)
    test.evolution(100)



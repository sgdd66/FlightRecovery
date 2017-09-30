#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

class Passenger(object):
    '''旅客类'''

    def __init__(self,id,flight,population):
        self.id=id
        self.flight=flight
        self.population=population
        self.status='waiting'

    def __cmp__(self, other):
        if self.__eq__(other):
            return 0
        elif self.__lt__(other):
            return -1
        elif self.__gt__(other):
            return 1

    def __eq__(self, other):
        if(self.population==other.population):
            return True
        else:
            return False

    def __lt__(self, other):
        if(self.population<other.population):
            return True
        else:
            return False

    def __gt__(self, other):
        if self.population>self.population:
            return True
        else:
            return False
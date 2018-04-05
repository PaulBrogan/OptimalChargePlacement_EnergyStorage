
## -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 14:18:39 2016

@author: Admin
"""

import CSVtoDict as c2d
#import matplotlib.pyplot as plt
#import IEEEformat
import numpy as np
#import bottleneck as bn


class Charger():
    def __init__(self):
        self.headers1 = ['Time', 'TimeHr', 'TimeInt', 'Power', 'SoC', 'Revenue']
        self.headers2 = ['opTime', 'tradeValue']

        self.ipFolder = 'ipData'
        self.opFolder = 'opData'
        
        self.ipList = ['2008.csv']
        self.batteryCapList = [0.5,5,50,500]#[10 + 2*n for n in range(4)] + [24 + 6*n for n in range(5)] + [96, 168, 672]#[0.5 + 0.5 * n for n in range(0, 5)] + [3 + n for n in range(0,6) ]
        
        self.tradingPeriod = 0.5
        self.startPrice = 500.
        self.acceptableDrop = 0.9
        self.minimumPriceList = [10]

    def initialise(self):

        self.Price = np.array(self.DataDict['Price'])
        self.DataLength = len(self.Price)
        
        self.Price = np.array(self.DataDict['Price'])
        self.Priceindex =  [ (i, self.Price[i]) for i in range(len(self.Price))]
        self.Priceindex = np.array(self.Priceindex, dtype = [('index', np.int32), ('Price', np.float32)])
        #   self.PriceMinMaxAbs does not change [timeIndex, sortIndex, Price] 
        self.PriceMinMaxAbs = np.sort(self.Priceindex, order = 'Price')
        self.PriceMinMaxAbs = np.array([( i, self.PriceMinMaxAbs[i][0], self.PriceMinMaxAbs[i][1] ) 
                    for i in range(len(self.Price))], 
                    dtype = [ ('timeIndex', np.int32), ('sortIndex', np.int32), ('Price', np.float32)])#, np.int32)

    def reinitialise(self): 
        self.CurrentPrice = self.startPrice
        self.chargePlacements = 0
        
        self.PriceMinMax = np.copy(self.PriceMinMaxAbs[:int(self.DataLength/2)])
        self.Pricetemp = np.copy(self.Price)
        self.DataDict['Length'] = self.DataLength
        self.fullCharge = self.batteryCap / self.tradingPeriod
        halfSoC = int(self.fullCharge/2)
        self.DataDict['SoC'] = np.array([halfSoC] * self.DataLength, dtype=np.int16)     #this will be between 0 and batteryCap / tradingPeriod
        self.DataDict['Power'] = np.zeros(self.DataLength, dtype=np.int16)     #this will be +1, 0 or -1   
        self.DataDict['Revenue'] = np.zeros(self.DataLength, dtype=np.float32)   #this is power x Price   
        self.DataDict['TimeInt'] = np.arange(self.DataLength, dtype = np.int32)    #this is time in hours / trading period
        self.DataDict['TimeHr'] = self.DataDict['TimeInt'] * self.tradingPeriod
        self.DataDict['tradeValue'] = []
        self.DataDict['Time'] = np.array(self.DataDict['Time'])
        

    def search(self, trialList, value):
        i = 0
        for val in np.nditer(trialList):
            if val == value:
                break
            i+=1
        return(i)

    def updateCharge(self, x, y, charge = 1):
        """the x value is the start time, the y value the finish time,
        the charge value is the change in the state of charge between the two times
        This updates power, revenue and state of charge"""
        update = True
        #print(x,y,charge)
        if self.DataDict['Power'][x] != 0:
            update = False
            print('1 wanted to charge at ', charge, ' but power already at ', self.DataDict['Power'][x], x, self.Pricetemp[x])
        if self.DataDict['Power'][y] != 0:
            update = False
            print('2 wanted to discharge at ', -charge, ' but power already at ', self.DataDict['Power'][y], y, self.Pricetemp[y])
            
        if charge == 1 and np.amax(self.DataDict['SoC'][x:y]) > self.fullCharge -1:
            update = False
            print('State of charge error - too high ', np.amax(self.DataDict['SoC'][x:y]), self.DataDict['SoC'][x:x+10], self.DataDict['SoC'][y-10:y])
            
        if charge == -1 and np.amin(self.DataDict['SoC'][x:y]) <= 0:
            update = False
            print('State of charge error - too low ', np.amin(self.DataDict['SoC'][x:y]))
            print(self.DataDict['SoC'][x:y])
        
        if update == True:
            self.DataDict['Power'][x] = charge
            self.DataDict['Power'][y] = -charge
            
            intro = self.DataDict['SoC'][:x]
            #filler1 = np.array([0.5 + self.DataDict['SoC'][x]])
            action = self.DataDict['SoC'][x:y+1] + charge
            #filler2 = np.array([0.5 + self.DataDict['SoC'][y]])
            outro = self.DataDict['SoC'][y+1:]  
            
            self.DataDict['SoC'] = np.concatenate((intro, action, outro))
            
            self.DataDict['Revenue'][x] = -charge * self.Price[x] * self.tradingPeriod
            self.DataDict['Revenue'][y] =  charge * self.Price[y] * self.tradingPeriod
            #print('charge placed')
            
        return(update)
            
        
    def oneScan(self):
        #self.PriceMinMaxTemp = np.copy(self.PriceMinMax)
        delIndex = []

        self.poistivePlacement = 0
        self.negativePlacement = 0
        index = -1
        for cArg in self.PriceMinMax:#Temp:
            """This steps through all the values starting with the lowest Price"""
            index += 1
            sortIndex, timeIndex, Price = cArg
            cMoney, dMoney = -999, -999
            #this is charge and discharge money
            #print(cArg)
            
            """This places a charge at timeIndex and sells it later"""
            if self.DataDict['SoC'][timeIndex] < self.fullCharge and timeIndex < self.DataLength:
                y = np.argmax(self.DataDict['SoC'][timeIndex:])
                #print(self.DataDict['SoC'][timeIndex + y], self.DataDict['SoC'][timeIndex + y - 5: timeIndex + y])
                if self.DataDict['SoC'][timeIndex + y] == self.fullCharge:
                    y = timeIndex + y
                else:
                    
                    #print('is there really no blockage before the end?', timeIndex, y)
                    y = self.DataLength
                
                if timeIndex != y:
                    """Thius means there is a list, not an error causing value"""
                    y = timeIndex + np.argmax(self.Pricetemp[timeIndex:y])
                    cMoney = self.Pricetemp[y]
                else:
                    """fail, -999 is a rediculously low return and will no be 
                    picked unless the minimum acceptable price is set stupid"""
                    cMoney = -999
                
            
            """This trys to steel some charge from before and repay it"""
            if self.DataDict['SoC'][timeIndex] > 0 and timeIndex > 0:
                """no point trying if the state of charge is zero already, or
                we are at the begining of the list"""
                x = np.argmin(self.DataDict['SoC'][:timeIndex][::-1])
                """find the next minimum, working backwards from the begining"""
                if x != 0 and timeIndex != 0:
                    if self.DataDict['SoC'][timeIndex - x -1] == 0:
                        """This means the charge previous is zero and this
                        blocks the charge borrowing, as expected"""
                        x = timeIndex - x
                    else:
                        
                        #print('minimum charge not zero', timeIndex, x, self.DataDict['SoC'][timeIndex - x -5: timeIndex - x +5])
                        x = 0
                else:
                    #print('naturally hit start of list', x, timeIndex, x > timeIndex)
                    x = timeIndex
                    
                
                if timeIndex != x:
                    #print( x, timeIndex)
                    x = x + np.argmax(self.Pricetemp[x:timeIndex])
                    dMoney = self.Pricetemp[x]
                    #print(dMoney)
                    #fgh
                else:
                    dMoney = -999
            
            if cMoney >= dMoney:
                #print('charge', cMoney - Price)
                if (cMoney - Price) * self.tradingPeriod >= self.CurrentPrice:
                    proceed = self.updateCharge(timeIndex, y, 1)
                    
                    if proceed == True:
                        self.chargePlacements += 1
                        self.poistivePlacement += 1
                        delIndex.append(index)
                        #print('from', timeIndex, self.DataDict['Price'][timeIndex])
                        #print('to', y, self.DataDict['Price'][y])
                        self.Pricetemp[y] = -999 
                        self.DataDict['tradeValue'].append((cMoney - Price) * self.tradingPeriod)
                        #print('value added up', (cMoney - Price) * self.tradingPeriod)
                    
            else:
                #print('discharge', cMoney - Price)
                if (dMoney - Price) * self.tradingPeriod >= self.CurrentPrice:
                    proceed = self.updateCharge(x, timeIndex, -1)
                    
                    if proceed == True:
                        self.chargePlacements += 1
                        self.negativePlacement += 1
                        delIndex.append(index)
                        #print('from', x, self.DataDict['Price'][x])
                        #print('to', timeIndex, self.DataDict['Price'][timeIndex])
                        self.Pricetemp[x] = -999 
                        self.DataDict['tradeValue'].append((dMoney - Price) * self.tradingPeriod)
                        #print('value added down', (dMoney - Price) * self.tradingPeriod)
                    
        self.PriceMinMax = np.delete(self.PriceMinMax, delIndex)
        #return(chargePlacements, poistivePlacement, negativePlacement)
        
    def completeScan(self):
        #additions = 1
        #while additions > 0:
        self.oneScan()
        print('charges placed =', self.chargePlacements, ' | +ve ',  self.poistivePlacement, ' | -ve ', self.negativePlacement, ' | Toats = ', self.poistivePlacement + self.negativePlacement)
            #additions = self.poistivePlacement + self.negativePlacement
            
    def reducePrice(self):
        while self.CurrentPrice >= self.minimumPrice:
            print('searching at €', self.CurrentPrice)
            
            self.completeScan()
            self.CurrentPrice = int(self.acceptableDrop * self.CurrentPrice)
            
            
    def dumpData(self, ipName):
        data = [self.DataDict[header] for header in self.headers1]
        c2d.ListToCSV(data, self.headers1, self.opFolder +'/StateOfCharge/' + ipName + 'minPrice' + str(self.minimumPrice) +'/Battery_' + str(self.batteryCap) + 'hr.csv')
        
        data = [ [i * self.tradingPeriod for i in range(len(self.DataDict['tradeValue']))], self.DataDict['tradeValue'] ]
        c2d.ListToCSV(data, self.headers2, self.opFolder +'/Trade/' + ipName + 'minPrice' + str(self.minimumPrice) +'/Battery_' + str(self.batteryCap) + 'hr.csv')
        

    def go(self):
        
        for ipName in self.ipList:
            self.DataDict = c2d.csvtodict(self.ipFolder + "/" + str(ipName))
            self.initialise()
            for self.minimumPrice in self.minimumPriceList:
                for self.batteryCap in self.batteryCapList:
                    self.reinitialise()
                    print('----------------------------------------------------')
                    print('checking battery capacity of ', self.batteryCap)
                    print('minimum price of ', self.minimumPrice)
                    self.reducePrice()
                    self.dumpData(ipName[:-4])

       
run = Charger()
run.go()

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import csv, os

def multicsvtodict(FName):
    DictData = {}
    fi = open(FName,"r")
    data = csv.reader(fi)
    data = [row for row in data]
    fi.close()
    
    FName = FName[(FName.find("\\") + 1):-4]
    print(FName)
    
    DictData[FName] ={}
    
    HdrDict = {}
    n = 0
    print(data[0])
    for Hdr in data[0]:
        HdrDict[n] = Hdr
        n += 1
        DictData[FName][Hdr] = []
    
    for row in data[1:]:
        n = 0
        for Val in row:
            DictData[FName][HdrDict[n]].append(float(Val))
            n +=1
            
    return(DictData)

def csvtodict(FName):
    print('importing', FName)
    DictData = {}
    #DictData['x'] = []
    #DictData['y'] = []
    fi = open(FName,"r")
    data = csv.reader(fi)
    data = [row for row in data]
    fi.close()
    
    HdrDict = {}
    n = 0
    print('headers', data[0])
    #DictData['Headers'] = data[0] 
    for Hdr in data[0]:
        HdrDict[n] = Hdr
        n += 1
        DictData[Hdr] = []
    
    for row in data[1:]:
        #DictData['x'].append(float(row[0]))
        n = 0
        for Val in row:
            DictData[HdrDict[n]].append(float(Val))
            #DictData[HdrDict[n]][row[0]] = float(Val)
            n +=1
            
    return(DictData)
    
def ListToCSV(Data, Header, Name):
    def write(Data, Header, Name):
        with open(str(Name) + '.csv', 'w', newline='') as fo:
            writer = csv.writer(fo)
            writer.writerow(Header)
            for n in range(0, len(Data[1])):
                row = []
                for D in Data:
                    try:
                        row.append(D[n])
                    except:
                        row.append('')
                writer.writerow(row)
                
    def makeDirectory(Name):
        print('make full directory', Name)
        Name.replace('\\', '/')
        index = Name.find('/')
        directory = ''
        while index > 0:
            directory += Name[:index+1]
            Name = Name[index+1:]
            if not os.path.exists(directory):
                os.makedirs(directory)
            index = Name.find('/')
            print('made', directory, Name)
            
    try:
        write(Data, Header, Name)
    except:
        makeDirectory(Name)
        write(Data, Header, Name)
            
            
        

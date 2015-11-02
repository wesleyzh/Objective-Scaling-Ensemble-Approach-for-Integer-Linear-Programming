"""
Dynamic Scaling Induced Neighborhood Search Model  version 1.0
Implemented by Weili Zhang, 2014/07/05

Input: 
yDict: all the binary solutions in Dynamic Binary Coefficient Scaling Procedure 
strategy: #1, pure last iteraionts; #2, pure tbest; #3, tbest plus closeest 2 solution; #4, tbest plust last cut; #5, tbest plust the first and the last 
cut: cut the last subset of all iterations
tBest: the best solution found in DBCSP
maxtime: maximum run time

Output:
new MBP problem after removing unused variables

"""
import copy

def DSINS(m, yDict, tBest, cut, maxTime, strategy = 1):
    
    model = m.copy()
    
    ##extract the variables
    #var = model.getVars()    #all the variables information, including name, type, lb, ub, obj
    #nvar = model.NumVars     #total number of variables
    
    #x = {}    #continuous variables
    #y = {}    #binary variables
    #c = {}    #coefficient of continuous variables
    #h = {}    #coefficient of binary variables
    
    ##check the type of variables, if the problem is not MBP, exit
    
    #NumBinVar, NumConVar = 0, 0
    
    #for i in range(nvar):
        #if var[i].vtype == "C":  #continuous variables
            #x[var[i].VarName] = model.getVarByName(var[i].VarName)   
            #c[var[i].VarName] = x[var[i].VarName].Obj
            #NumConVar += 1
        #elif var[i].vtype == "B":  #binary variables
            #y[var[i].VarName] = model.getVarByName(var[i].VarName)
            #h[var[i].VarName] = y[var[i].VarName].Obj
            #NumBinVar += 1
        #elif var[i].vtype == "B":  #integer variables
            #print "\nUser Error: variables contain integer variables, this is not a MBP problem\n"
            #exit(1)             
    
    #if NumBinVar == 0:
        #print "\nUser Error: variables does not contain binary variables, this is not a MBP problem\n"
        #exit(1)         
    
    #if NumConVar == 0:
        #print "\nUser Error: variables does not contain continuous variables, this is not a MBP problem\n"
        #exit(1)        
    
    
    nyDict = {}  #sub dictionay of yDict based on different strategies
    
    if strategy == 1:
        if cut > len(yDict.keys()):
            print "\nUser Error: the number of last iterations exceed the total number of iteraions\n"
            exit(1) 
        else:
            for j in xrange(cut):
                nyDict[len(yDict)-j] = copy.deepcopy(yDict[len(yDict)-j])            
    elif strategy == 2:
        nyDict[tBest] = copy.deepcopy(yDict[tBest])  
    elif strategy == 3:
        nyDict[tBest] = copy.deepcopy(yDict[tBest])
        if tBest == 1:                                                      #tBest is the first iteration
            if tBest +2 <= len(yDict.keys()):
                nyDict[tBest+1] = copy.deepcopy(yDict[tBest+1])
                nyDict[tBest+2] = copy.deepcopy(yDict[tBest+2])
            else:
                print "\nUser Error: the number of selected iterations exceed the total number of iteraions\n"
                exit(1)                 
        elif tBest == len(yDict):                                     #tBest is the bottom iteration
            if tBest - 2 >=  1:
                nyDict[tBest-1] = copy.deepcopy(yDict[tBest-1])
                nyDict[tBest-2] = copy.deepcopy(yDict[tBest-2]) 
            else:
                print "\nUser Error: the number of selected iterations exceed the total number of iteraions\n"
                exit(1)                
        else:
            nyDict[tBest+1] = copy.deepcopy(yDict[tBest+1])
            nyDict[tBest-1] = copy.deepcopy(yDict[tBest-1])   
    elif strategy == 4:        
        nyDict[tBest] = copy.deepcopy(yDict[tBest]) 
        if cut > len(yDict.keys()):
            print "\nUser Error: the number of last iterations exceed the total number of iteraions\n"
            exit(1)         
        else:
            for j in xrange(cut):
                nyDict[len(yDict)-j] = copy.deepcopy(yDict[len(yDict)-j])  
    elif strategy == 5:
        nyDict[tBest] = copy.deepcopy(yDict[tBest]) 
        nyDict[len(yDict)] = copy.deepcopy(yDict[len(yDict)]) 
        nyDict[1] = copy.deepcopy(yDict[1])
        
    #analyze the agreement within all the solutions in nyDict
    agree = {}
    for j in nyDict.keys():
        for z in nyDict[j].keys():
            if nyDict[j][z] != 0 and z not in agree.keys():
                agree[z] = 1
            elif nyDict[j][z] != 0 and z in agree.keys():
                agree[z] += 1
            elif nyDict[j][z] == 0 and z not in agree.keys():
                agree[z] = 0
            elif nyDict[j][z] == 0 and z in agree.keys():
                pass     
            
    return agree

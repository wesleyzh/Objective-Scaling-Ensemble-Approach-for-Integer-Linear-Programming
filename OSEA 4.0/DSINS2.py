"""
Dynamic Scaling Induced Neighborhood Search Model  version 2.0
Implemented by Weili Zhang, 2014/07/05

Input: 
yDict: all the binary solutions in Dynamic Binary Coefficient Scaling Procedure 
strategy: #1, pure last iteraionts; #2, pure tbest; #3, tbest plus closeest 2 solution; #4, tbest plust last cut; #5, tbest plust the first and the last 
cut: cut the last subset of all iterations; #6, rank all the solutions, best, worst, and medium

tBest: the best solution found in DBCSP
maxtime: maximum run time

Output:
new MBP problem after removing unused variables

Updates:
- strategy 6 is added, selection based on objective values

"""
import copy

def DSINS(m, yDict, objDict, tBest, cut, strategy = 1):
    
    model = m.copy()   
    
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
    
    elif strategy == 6:
        """new strategy, rank all the solutions based on true objective
           select the best, medium, worst
        """
        
        obj_sol = {}
        
        #create new dictionary with obj: solution
        for key in yDict.keys():
            
            obj_sol[objDict[key]] = yDict[key]
            
        #rank the obj
        objective_list = obj_sol.keys()
        sorted(objective_list)
        
        nyDict[0] = copy.deepcopy(obj_sol[objective_list[0]])  #best
        nyDict[len(objective_list)-1] =  copy.deepcopy(obj_sol[objective_list[len(objective_list)-1]])  #worst
        nyDict[len(objective_list)/2] =  copy.deepcopy(obj_sol[objective_list[len(objective_list)/2]])  #medium
        
        
        
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

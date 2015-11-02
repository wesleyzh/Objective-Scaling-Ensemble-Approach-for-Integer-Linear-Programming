"""
Dynamic Binary Coefficient Slope Scaling Procedure Model  version 2.0
An important part in OSEA

Implemented by Weili Zhang, 2015/06/05

Input: 
m: mixed binary programming model 
p: power of the scaling parameter
psi: parameter to linearize the coefficient
maxtime: maximum run time

Output:
All Solutions appeared in all iteraions

Algorithm

1, remove the binary constraint
2, modify the binary coeeficient
3, start the procedure
4, stop until binary solution does not change

"""


from gurobipy import *
import time
import copy
import math

def DBCSP (m, maxTime, psi, p, M_switicher):
    Change = True    #used to determine if DSSP loop should continue -- specifically: has there been any changes to the solution vector
    
    t= 0             #keeps track of total iterations
    
    bestObj = float("infinity")   #stores the best objective value found
    
    tempSolution = {} # used for defining stopping condition 
    
    mod = m.copy()  #copy the original MBP model
    mod.setParam( 'OutputFlag', 0)  
    mod.params.threads = 1    
    
    #extract the variables
    var_l = mod.getVars()    #all the variables information, including name, type, lb, ub, obj
    nvar_l = mod.NumVars     #total number of variables
    
    x_l = {}    #local continuous variables
    y_l = {}    #local binary variables
    c_l = {}    #local coefficient of continuous variables
    h_l = {}    #local coefficient of binary variables
    
    #check the type of variables, if the problem is not MBP, exit
    
    NumBinVar, NumConVar, NumIntVar = 0, 0, 0
    
    for i in range(nvar_l):
        if var_l[i].vtype == "C":  #continuous variables
            x_l[var_l[i].VarName] = mod.getVarByName(var_l[i].VarName)   
            c_l[var_l[i].VarName] = x_l[var_l[i].VarName].Obj
            NumConVar += 1
        elif var_l[i].vtype == "B":  #binary variables
            y_l[var_l[i].VarName] = mod.getVarByName(var_l[i].VarName)
            h_l[var_l[i].VarName] = y_l[var_l[i].VarName].Obj
            NumBinVar += 1
        elif var_l[i].vtype == "I":  #integer variables
            if var_l[i].lb == 0 and var_l[i].ub == 1:
                y_l[var_l[i].VarName] = mod.getVarByName(var_l[i].VarName)
                h_l[var_l[i].VarName] = y_l[var_l[i].VarName].Obj           
                NumBinVar += 1
            else:
                y_l[var_l[i].VarName] = mod.getVarByName(var_l[i].VarName)
                h_l[var_l[i].VarName] = y_l[var_l[i].VarName].Obj           
                NumIntVar += 1                           
    
    #if NumBinVar == 0:
        #if NumIntVar == 0:
            #print "\nUser Error: variables does not contain binary/interger variables\n"
            #exit(1)         
    
    
    #initialize the binary coeffecients
    #intial linearized cost: h_j/M
    
    if M_switicher == 1:
        
        M = sum(h_l.values())
        
        #M = quicksum(h_l[i] for i in h_l.keys())
        
    elif M_switicher == 2:
        M = 1 # max(h_l.values())
    
        
    
    for i in y_l.keys():
        y_l[i].vType = GRB.CONTINUOUS
        #y_l[i].lb, y_l[i].ub = 0, 1  #make sure the binary variable is constrained within 0 and 1
        y_l[i].Obj = float(psi*h_l[i]/M)  #initialize the binary coeffecients
        tempSolution[i] = -1
    

    M = 1
    
    mod.params.timeLimit = maxTime
    mod.update()
        
    start = time.clock()
    
    yDict = {}   #dictionary of all the solutions
    objDict = {}  #dictionaly of objective values of all solutions
    
    #save the solutions
    #g = open('DBCSP_psi{}_p{}.txt'.format(psi,p),'w')
    #g.close()    
    
    while Change == True:    
                
        t += 1            #increment iteration count
                
        mod.optimize()      #call GUROBI to solve the model   
        if  NumConVar != 0:          
            x_solution = mod.getAttr('x', x_l)  # the solution x vector
        y_solution = mod.getAttr('x', y_l)  # the solution y vector
        
        y_integer_solution = {}
        for key in y_l.keys():
            
            if y_solution[key] > 0.000001:
                
                y_integer_solution[key] = math.ceil(y_solution[key])
            
            else:
                y_integer_solution[key] = 0
        
        
        ObjectiveVal =  quicksum(c_l[i]*x_solution[i] for i in x_l.keys()) + \
            quicksum(h_l[i]*y_integer_solution[i] for i in y_l.keys()) #calculate the true objective cost
        ObjectiveVal =  ObjectiveVal.getValue()
        
        
        yDict[t] = copy.deepcopy(y_solution)
        objDict[t] = ObjectiveVal
        
        #print max(yDict[t].values())
        
        if ObjectiveVal < bestObj:   #obtain the best solution in DBSCP
            bestObj = ObjectiveVal             
            tbest = t
        
        processtime = time.clock() - start    
        if processtime > maxTime:
            break           
            
        Change = False    
        #evaluate the binary variables from the solution to update the linearized cost function
        for i in y_l.keys():
            
            if y_solution[i] != tempSolution[i]:    # if any update occurs, continue
                Change = True            
                
            if y_solution[i] > 0.00001:         
                               
                if y_l[i].Obj != float(psi*h_l[i]/((M*y_solution[i]+1)**p)):    # if the cost coefficient should be updated,
                    y_l[i].Obj =  float(psi*h_l[i]/((M*y_solution[i]+1)**p))      # update: h_i / y_ik
                                                                             
        tempSolution = copy.deepcopy(y_solution)
        
        processtime = time.clock() - start
        
        if processtime > maxTime:
            break          
        
               
    
    presult = [t, bestObj, tbest, yDict, objDict]   #list of total iterations used, best "p" value, and best objective found 
    
    return presult                  #return the list    
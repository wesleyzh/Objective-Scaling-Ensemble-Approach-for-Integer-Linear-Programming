"""
Combine Dynamic Binary Coefficient Scaling Procedure Model v1.0 and 
Dynamic Scaling Induced Neighborhood Search Model v1.0 to solve general MBP problem

implemented by weili zhang, 2014/07/05

DSINS 2.0 could be applied to BP, MBP, IP, MIP

"""
#standard libaries
from __future__ import division
import operator
import time
from numpy import * 
import math
from gurobipy import *
import random
import copy


#modules input
import DBCSPmodule as DBCSP
import DSINSmodule as DSINS

def Analysis_Solution(ite, sol, optsol):
    
    global OptimalSolution
    
    zeros, between, ones = 0,0,0
    hamming = 0
    
    for pp in sol.keys():
        if OptimalSolution == 1:
            hamming += abs(sol[pp] - optsol[pp])  #compute the hamming distance
        else:
            hamming = -1
        if sol[pp] == 0:
            zeros += 1      #compute the zeros
        elif sol[pp] == 1:
            ones += 1       #compute the ones
        else:
            between += 1    #compute the 0~1
          
    #save as iteration, 0, 0~1, 1, hamming
    f1 = open('{}_Analysis_M{}__psi{}_p{}.txt'.format( m.ModelName, M_switicher, psi,p),'a')
    f1.write('{},{},{},{},{}\n'.format(ite,zeros, between, ones,hamming))
    f1.close()
    

#m = read('F:/OU/Research Projects/Active/MBP heuristic/MBP benchmarks/Easy/aflow40b')  #read MBP model from mps file
#m = read('C:/Users/nich8038/Dropbox/Grad Students/ISE - Zhang, Weili/Research Projects/Active/MBP heuristic/Easy/aflow40b')

#*******************************************************************
#DBCSP settings
plist =[0.5,2.0]  #power list
maxTime1 = 3600
psilist = [1.0] #psi values
M_switicher = 1 #1, sum; #2, max

#DSINS settings
cut = 3
maxTime2 = 3600
strategy = 5 

OptimalSolution = 1 #whether or not use GUROBI to solve the problem optimally



#read files
file = open('namelist.txt','r')
namelist = []
for line in file:
    namelist.append(line)
file.close()

#name = namelist[0].rstrip()   #remove the \n
#print 'C:/Users/zhan4402/Desktop/MBP heuristic/MBP benchmarks/{}'.format(name)
#m = read('C:/Users/zhan4402/Desktop/MBP heuristic/MBP benchmarks/{}'.format(name))


#*******************************************************************

#MBPname, GRBobj, GRBTime, Agree0, AgreeOpen, Agree1, DSINSoBJ, Time1, Time2, TotTime
f = open('DBCSP_InOne.txt','a')  
#f.write('MBPname,Agree0, AgreeOpen, Agree1, DSINSobj, Time1, Time2, TotTime, M, psi, power, \n')
f.write('\n')
f.close()

for name in namelist:
    
    name = name.rstrip()   #remove the \n
    m = read('C:/Users/zhan4402/Desktop/MBP heuristic/MBP benchmarks/{}'.format(name))
    #m = read('C:/Users/zhan4402/Desktop/MBP heuristic/Extra Instances/{}'.format(name))
    print 'name', name, '\n'
    
    m.setParam( 'OutputFlag', 1) 
    m.setParam( 'LogToConsole', 0 )
    m.setParam( 'LogFile', "" )   
    m.params.threads = 7
    m.params.NodefileStart = 0.5
    m.params.timeLimit = 600
    
    
    #extract the variables
    var = m.getVars()    #all the variables information, including name, type, lb, ub, obj
    nvar = m.NumVars     #total number of variables
    
    x = {}    #continuous variables
    y = {}    #binary variables
    c = {}    #coefficient of continuous variables
    h = {}    #coefficient of binary variables
    
    #check the type of variables, if the problem is not MBP, exit
    
    NumBinVar, NumConVar, NumIntVar = 0, 0, 0
    
    sum_coe = 0
    
    for i in range(nvar):
        if var[i].vtype == "C":  #continuous variables
            #print var[i].vtype, var[i].Obj, var[i].VarName
            pass
            x[var[i].VarName] = m.getVarByName(var[i].VarName)   
            c[var[i].VarName] = x[var[i].VarName].Obj
            NumConVar += 1
        elif var[i].vtype == "B":  #binary variables
            #print var[i].vtype, var[i].Obj, var[i].VarName
            sum_coe += var[i].Obj
            pass
            y[var[i].VarName] = m.getVarByName(var[i].VarName)
            h[var[i].VarName] = y[var[i].VarName].Obj
            NumBinVar += 1
        elif var[i].vtype == "I":  #integer variables
            if var[i].lb == 0 and var[i].ub == 1:
                #print var[i].vtype, var[i].Obj, var[i].VarName
                y[var[i].VarName] = m.getVarByName(var[i].VarName)
                h[var[i].VarName] = y[var[i].VarName].Obj
                NumBinVar += 1
                sum_coe += var[i].Obj
            else:
                y[var[i].VarName] = m.getVarByName(var[i].VarName)
                h[var[i].VarName] = y[var[i].VarName].Obj            
                NumIntVar += 1
                sum_coe += var[i].Obj
                #print var[i].VarName, var[i].vType, var[i].lb, var[i].ub
                #exit(1)             
    
    if NumBinVar == 0:
        if NumIntVar == 0:
            print "\nUser Error: variables does not contain binary/interger variables\n"
            #exit(1) 
            continue
            
    if sum_coe == 0 :
        print "\nUser Error: all the binary/integer coefficients are zero\n"
        #exit(1)
        continue
    
    if OptimalSolution == 1:
        
        try:
            
            #solve the problem with GRB
            m.optimize()    
            if  m.status == 2 or m.status == 9:
                #get the optimal solutions 
                OptBinSol = m.getAttr('x', y) 
                GRBOptTime = m.Runtime
                print "GRB Optimal", m.objval,GRBOptTime
                f = open('DBCSP_InOne.txt','a')  
                f.write('{}, {}, {},'.format( m.ModelName,m.objval, GRBOptTime))
                f.close()    
            
            else:
                f = open('DBCSP_InOne.txt','a')  
                f.write('{}, NA, 3600,'.format( m.ModelName))
                f.close()     
        except GurobiError:
            f = open('DBCSP_InOne.txt','a')  
            f.write('{}, NA, 3600,'.format( m.ModelName))
            f.close()        
            
    else:
        OptBinSol = -1
        f = open('DBCSP_InOne.txt','a')  
        f.write('{}, NA, NA,'.format( m.ModelName))
        f.close()   
           
    #m.reset()
    
    ##get a feasible solution with gurobi 
    #m.params.timeLimit = 10
    #try:
        #m.optimize()
        #if  m.status == 2 or m.status == 9:
            #if NumConVar != 0 :
                #gx_solution = m.getAttr('x', x)  # the solution x vector
            #gy_solution = m.getAttr('x', y)  # the solution y vector
            #gObjectiveVal = m.objval
            #print gObjectiveVal
                
        #else:
            #print "\nUser Error: GUROBI can not find fieasible solution in 10s\n"
            ##exit(1) 
            #f = open('DBCSP_InOne.txt','a') 
            #f.write('GUROBI can not find fieasible solution ion 10s\n')
            #f.close()                
            #continue
                
    
    #except GurobiError:
        #print "\nGUROBI Error: GUROBI can not find fieasible solution ion 10s\n"
        ##exit(1) 
        #f = open('DBCSP_InOne.txt','a') 
        #f.write('GUROBI can not find fieasible solution ion 10s\n')
        #f.close()            
        #continue
    
        
    #m.params.timeLimit = 8
    #m.reset()
        
    #final_agree = {}  #the agree dictionary contains all the psi values
    
    #totIteration = 0   #total iterations in all psi*DBCSP
    #best_iteration = {}  #best iteration for each psi value
    #all_yDict = {}
    #all_agree = {}
    
    #start_time = time.clock()
    
    #for p in plist:
    
        #for psi in psilist:
            
            #result1 = DBCSP.DBCSP(m, maxTime1, psi, p,M_switicher)
            
            #totIteration += result1[0]
            #best_iteration[p,psi] = result1[2]
            #all_yDict[p,psi] = copy.deepcopy(result1[3])
            
            #f1 = open('{}_Analysis_M{}__psi{}_p{}.txt'.format(m.ModelName, M_switicher, psi,p),'w')
            #f1.close()    
            
            
            #for i in all_yDict[p,psi].keys(): 
                #Analysis_Solution(i,all_yDict[p,psi][i], OptBinSol)
              
            
            #result2 = DSINS.DSINS(m, all_yDict[p,psi], best_iteration[p,psi], cut, maxTime2, strategy)
        
            
            #all_agree[p,psi] = copy.deepcopy(result2)
        
    
    ##agree_one = copy.deepcopy(all_agree[plist[0],psilist[0]])
    #agree_one = {}
    
    #for i in all_agree.keys():
        #for j in all_agree[i].keys():
            #agree_one[j] = 0  #create an empty agree_one dictionary
    
    #for i in all_agree.keys():
        #for j in all_agree[i].keys():
            #agree_one[j] += all_agree[i][j]  #update the agree dictionaries for all psi values
                    
    #for i in gy_solution.keys():
        #if gy_solution[i] > 0.0000001:
            #agree_one[i] += 1
            
    #RunTime1 = time.clock() - start_time
    #print RunTime1
       
    ##compute the performance of reducing the search space 
    #if strategy == 1:
        #ntotaliter = cut*len(psilist) + 1
    #elif strategy == 2:
        #ntotaliter = len(psilist) + 1
    #elif strategy == 3:
        #ntotaliter = 3*len(psilist) + 1
    #elif strategy == 4:
        #ntotaliter = (1+cut)*len(psilist) + 1
    #elif strategy == 5:
        #ntotaliter = 3*len(psilist) + 1
        
    #total1 = 0   
    #totalopen = 0  
    #total0 = 0
    
    #for i,j in agree_one.items():
        #if j == ntotaliter:
            #total1 += 1
        #elif j == 0:
            #total0 += 1    
        #else:
            #totalopen += 1
    
    #totalopen = totalopen + total1    
    
    #f = open('DBCSP_InOne.txt','a')  
    #f.write('{}, {}, {},'.format(total0,totalopen,total1))
    #f.close()   
    
    ##add constraints to fix those unused variables to zero
    #for i in agree_one.keys():
        #if agree_one[i] == 0:
            #m.addConstr(y[i] == 0.0,'Unused_%s' % (i)) 
          
    #m.update()
    
    #try:
        
        #m.optimize()
        
        #if  m.status == 2 or m.status == 9:
            #if NumConVar != 0:
                #x_solution = m.getAttr('x', x)  # the solution x vector
            #y_solution = m.getAttr('x', y)  # the solution y vector
            #ObjectiveVal = m.objval
            #RunTime2 = m.Runtime
            #print ObjectiveVal, RunTime2
            #f = open('DBCSP_InOne.txt','a')  
            #f.write('{}, {}, {}, {},{},{},{}\n'.format(ObjectiveVal,RunTime1,RunTime2, RunTime1+RunTime2,M_switicher,psilist,plist))
            #f.close()             
            
        #else:
            #print "\nUser Error: GUROBI can not find fieasible solution in 300s\n"
            ##exit(1) 
            #f = open('DBCSP_InOne.txt','a') 
            #f.write('GUROBI can not find fieasible solution in 300s\n')
            #f.close()            
            #continue
            
      
            
    #except GurobiError:
        #print('Error reported')       
        
    


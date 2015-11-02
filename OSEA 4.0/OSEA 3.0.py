"""
Combine Dynamic Binary Coefficient Scaling Procedure Model v1.0 and 
Dynamic Scaling Induced Neighborhood Search Model v1.0 to solve general MBP problem

implemented by weili zhang, 2014/07/05

OSEA 3.0 could be applied to BP, MBP, IP, MIP
removed M

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
import datetime


#modules input
import DBCSPmodule as DBCSP
import DSINSmodule as DSINS

# Define callback function

def mycallback(model, where):
    if where == GRB.callback.PRESOLVE:
        # Presolve callback
        #print('Removed %d columns and %d rows' % \
              #(model.cbGet(GRB.callback.PRE_COLDEL), \
               #model.cbGet(GRB.callback.PRE_ROWDEL)))
        pass
    elif where == GRB.callback.SIMPLEX:
        # Simplex callback
        #itcnt = model.cbGet(GRB.callback.SPX_ITRCNT)
        #if itcnt - model._lastiter >= 100:
            #model._lastiter = itcnt
            #obj  = model.cbGet(GRB.callback.SPX_OBJVAL)
            #pinf = model.cbGet(GRB.callback.SPX_PRIMINF)
            #dinf = model.cbGet(GRB.callback.SPX_DUALINF)
            #pert = model.cbGet(GRB.callback.SPX_ISPERT)
            #if pert == 0:
                #ch = ' '
            #elif pert == 1:
                #ch = 'S'
            #else:
                #ch = 'P'
            #print('%d %g %s %g %g' % (int(itcnt), obj, ch, pinf, dinf))
        pass
    elif where == GRB.callback.MIP:
        # General MIP callback
        #nodecnt = model.cbGet(GRB.callback.MIP_NODCNT)
        #if nodecnt - model._lastnode >= 100:
            #model._lastnode = nodecnt
            #objbst = model.cbGet(GRB.callback.MIP_OBJBST)
            #objbnd = model.cbGet(GRB.callback.MIP_OBJBND)
            #elapsed_time =  model.cbGet(GRB.callback.RUNTIME)
            ##print('%d %g %g' % (int(nodecnt), objbst, objbnd)), elapsed_time          
        #if nodecnt > model._mynodelimit:
            #model.terminate()
        pass
    elif where == GRB.callback.MIPSOL:
        # MIP solution callback
        obj     = model.cbGet(GRB.callback.MIPSOL_OBJ)
        nodecnt = int(model.cbGet(GRB.callback.MIPSOL_NODCNT))
        elapsed_time =  model.cbGet(GRB.callback.RUNTIME)
        print('*** New solution at node %g, time %g, objective %g' % (nodecnt, elapsed_time, obj))
        sys.exit("First feasible solution is found")
        #print(model.cbGetSolution(model.getVars()))
        pass
    elif where == GRB.callback.MIPNODE:
        # MIP node callback
        #print('*** New node')
        #if model.cbGet(GRB.callback.MIPNODE_STATUS) == GRB.status.OPTIMAL:
            #x = model.cbGetNodeRel(model.getVars())
            #model.cbSetSolution(model.getVars(), x)
        pass


def Analysis_Solution(ite, sol, optsol):
    
    analyze_open = 0
    
    zeros, between, ones = 0,0,0
    hamming = 0
    
    for pp in sol.keys():
        if analyze_open == 1:
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
#OSEA settings
plist =[2.0]  #power list
psilist = [1.0] #psi values
Time_Limit = 600
maxTime1 = 100/len(psilist)
M_switicher = 1 #1, sum; #2, max
feasible_open = 1  #wether or not employ the feasible solution
OSEA = 1  #whether or no run OSEA

#DSINS settings
cut = 3
maxTime2 = 10
strategy = 5 

OptimalSolution = 1 #whether or not use GUROBI to solve the problem optimally
GRB = 1  #whether or no run GUROBI to solve original problem


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
f = open('OSEA_InOne.txt','a')  
#f.write('MBPname,Agree0, AgreeOpen, Agree1, DSINSobj, Time1, Time2, TotTime, M, psi, power, \n')
f.write('------{}-------\n'.format(datetime.datetime.now()))
f.close()

for name in namelist:
    
    name = name.rstrip()   #remove the \n
    m = read('C:/Users/zhan4402/Desktop/MBP heuristic/MBP benchmarks/{}'.format(name))
    #m = read('C:/Users/zhan4402/Desktop/MBP heuristic/Extra Instances/{}'.format(name))
    print 'name', name, '\n'
    
    m.setParam( 'OutputFlag', 0) 
    m.setParam( 'LogToConsole', 0 )
    m.setParam( 'LogFile', "" )   
    m.params.threads = 7
    m.params.NodefileStart = 0.5
    m.params.timeLimit = 300
    
    f = open('OSEA_InOne.txt','a')  
    #f.write('MBPname,Agree0, AgreeOpen, Agree1, DSINSobj, Time1, Time2, TotTime, M, psi, power, \n')
    f.write('{}, \n'.format(name))
    f.close()    
    
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
    
    
    if OSEA == 1:
    
        #get a feasible solution with gurobi 
        if feasible_open == 1:
            m.params.timeLimit =60  #time limit for the feasible solution
            try:
                m.optimize()
                if  m.status == 2 or m.status == 9:
                    if NumConVar != 0 :
                        gx_solution = m.getAttr('x', x)  # the solution x vector
                    gy_solution = m.getAttr('x', y)  # the solution y vector
                    gObjectiveVal = m.objval
                    print gObjectiveVal
                        
                else:
                    print "\nUser Error: GUROBI can not find fieasible solution in 1s\n"
                    #exit(1) 
                    f = open('OSEA_InOne.txt','a') 
                    f.write('NoSol')
                    f.close()                
                    #continue
                    feasible_open = 0
                        
            
            except GurobiError:
                print "\nGUROBI Error: GUROBI can not find fieasible solution ion 1s\n"
                #exit(1) 
                f = open('OSEA_InOne.txt','a') 
                f.write('NoSol')
                f.close()            
                #continue
                feasible_open = 0
        
            
        
        m.reset()
            
        final_agree = {}  #the agree dictionary contains all the psi values
        
        totIteration = 0   #total iterations in all psi*OSEA
        best_iteration = {}  #best iteration for each psi value
        all_yDict = {}
        all_agree = {}
        
        start_time = time.clock()
        
        for p in plist:
        
            for psi in psilist:
                
              
                result1 = DBCSP.DBCSP(m, maxTime1, psi, p,M_switicher)
               
               
                totIteration += result1[0]
                best_iteration[p,psi] = result1[2]
                all_yDict[p,psi] = copy.deepcopy(result1[3])
                
                f1 = open('{}_Analysis_M{}__psi{}_p{}.txt'.format(m.ModelName, M_switicher, psi,p),'w')
                f1.close()    
                
                OptBinSol = -1
                
                for i in all_yDict[p,psi].keys(): 
                    Analysis_Solution(i,all_yDict[p,psi][i], OptBinSol)
                  
                RunTime1 = time.clock() - start_time
                print RunTime1  
                
                result2 = DSINS.DSINS(m, all_yDict[p,psi], best_iteration[p,psi], cut, maxTime2, strategy)
                
                print "Ensemble time", time.clock() - RunTime1 
            
                
                all_agree[p,psi] = copy.deepcopy(result2)
            
        
        #agree_one = copy.deepcopy(all_agree[plist[0],psilist[0]])
        agree_one = {}
        
        for i in all_agree.keys():
            for j in all_agree[i].keys():
                agree_one[j] = 0  #create an empty agree_one dictionary
        
        for i in all_agree.keys():
            for j in all_agree[i].keys():
                agree_one[j] += all_agree[i][j]  #update the agree dictionaries for all psi values
                        
        if feasible_open == 1:
            for i in gy_solution.keys():
                if gy_solution[i] > 0.0000001:
                    agree_one[i] += 1
                
       
        
        if RunTime1 < Time_Limit :
            m.params.timeLimit = Time_Limit - RunTime1
        else:
            m.params.timeLimit = 10
           
        #compute the performance of reducing the search space 
        if strategy == 1:
            ntotaliter = cut*len(psilist) + 1
        elif strategy == 2:
            ntotaliter = len(psilist) + 1
        elif strategy == 3:
            ntotaliter = 3*len(psilist) + 1
        elif strategy == 4:
            ntotaliter = (1+cut)*len(psilist) + 1
        elif strategy == 5:
            ntotaliter = 3*len(psilist) + 1
            
        total1 = 0   
        totalopen = 0  
        total0 = 0
        
        for i,j in agree_one.items():
            if j == ntotaliter:
                total1 += 1
            elif j == 0:
                total0 += 1    
            else:
                totalopen += 1
        
        totalopen = totalopen + total1    
        
        f = open('OSEA_InOne.txt','a')  
        f.write('{}, {}, {}, {},'.format(name, total0,totalopen,total1))
        f.close()   
        
        #add constraints to fix those unused variables to zero
        for i in agree_one.keys():
            if agree_one[i] == 0:
                m.addConstr(y[i] == 0.0,'Unused_%s' % (i)) 
              
        m.update()
        
        m.reset()
        
        try:
            print "Gurobi solve the sub_ILP starts..."
            #m.optimize(mycallback)
            #m.params.timeLimit = 600 - RunTime2
            m.optimize()
            
            
            if  m.status == 2 or m.status == 9:
                if NumConVar != 0:
                    x_solution = m.getAttr('x', x)  # the solution x vector
                y_solution = m.getAttr('x', y)  # the solution y vector
                ObjectiveVal = m.objval
                RunTime2 = m.Runtime
                print ObjectiveVal, RunTime2
                f = open('OSEA_InOne.txt','a')  
                f.write('{}, {}, {}, {}, {}, {} '.format(ObjectiveVal,RunTime1,RunTime2, RunTime1+RunTime2,psilist,plist))
                f.close()             
                
            else:
                print "\nUser Error: GUROBI can not find fieasible solution in 300s"
                #exit(1) 
                f = open('OSEA_InOne.txt','a') 
                f.write('GUROBI can not find fieasible solution in 300s')
                f.close()            
                continue
                
          
                
        except GurobiError:
            print('Error reported')  
        
    
    #use GUROBI to solve the same problem with same time 
    if GRB == 1:
        m2 = read('C:/Users/zhan4402/Desktop/MBP heuristic/MBP benchmarks/{}'.format(name))
        m2.setParam( 'OutputFlag', 1) 
        m2.setParam( 'LogToConsole', 0 )
        m2.setParam( 'LogFile', "" )   
        m2.params.threads = 7
        m2.params.NodefileStart = 0.5
        m2.params.timeLimit = RunTime1+RunTime2 + 1
    
        print "GRB solve the original problem starts..."
        try:
            #m2.optimize(mycallback)
            m2.optimize()
            if  m2.status == 2 or m2.status == 9:
                GRBOptTime = m2.Runtime
                print "GRB Same Time Solution", m2.objval,GRBOptTime
                f = open('OSEA_InOne.txt','a')  
                f.write('{}, {}, {} \n'.format( m2.ModelName,m2.objval, GRBOptTime))
                f.close()    
                    
            else:
                f = open('OSEA_InOne.txt','a')  
                f.write('{}, NoSol, {} \n'.format( m2.ModelName, RunTime1+RunTime2))
                f.close()     
       
        except GurobiError:
            f = open('OSEA_InOne.txt','a')  
            f.write('{}, NoSol, {} \n'.format( m2.ModelName, RunTime1+RunTime2))
            f.close() 
        
    #if OptimalSolution == 1:
           
        #try:
            
            ##solve the problem with GRB
            #m.optimize()    
            ##if  m.status == 2 or m.status == 9:
            ##get the optimal solutions 
            #OptBinSol = m.getAttr('x', y) 
            #GRBOptTime = m.Runtime
            #print "GRB Optimal", m.objval,GRBOptTime
            #f = open('OSEA_InOne.txt','a')  
            #f.write('{}, {}, {} \n'.format( m.ModelName,m.objval, GRBOptTime))
            #f.close()    
            
            ##else:
                ##f = open('OSEA_InOne.txt','a')  
                ##f.write('{}, NA, 3600 \n'.format( m.ModelName))
                ##f.close()     
        #except GurobiError:
            #f = open('OSEA_InOne.txt','a')  
            #f.write('{}, NA, 3600 \n'.format( m.ModelName))
            #f.close()        
            
    #else:
        #OptBinSol = -1
        #f = open('OSEA_InOne.txt','a')  
        #f.write('{}, NA, NA \n'.format( m.ModelName))
        #f.close()   

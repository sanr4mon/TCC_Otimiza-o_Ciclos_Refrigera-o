# -*- coding: utf-8 -*-
"""
Created on Sat May 13 21:00:16 2023

@author: Ramon
"""

import random
import math
import matplotlib.pyplot as plt
import numpy as np
import CoolProp as cp
from CoolProp.CoolProp import PropsSI
from COP_Duplo_Estagio import COP_Duplo_Estagio_Compress
 

#Parâmetros

maxit = 101
npop = 100
w = 1.0
c1 = 2
c2 = 2
damp = 0.99
rand = 0.01 * random.randint(0,100)
min_w = 0.3

mode = 1

VarMin = [0.35,-5 + 273.15, 1, 1]
VarMax = [0.65,5 + 273.15, 10, 10]

#Inicialização:
    
cycle_inputs = {
    't_external': 293,
    't_cond': 303,
    #'t_internal_g': 278,
    't_internal_f': 250,
    'Q_ETB': 35200,  # 10 TR
    'N_isent': 0.7,
    'refrigerant': 'R600A',
    # 'P_ETB':100000,#100 kPa
    #'tit_evap_g': 0.6,
    #'subcooling': 5,
    #'superheating': 5
}


def func1(x,y,z,w):
    cycle_inputs['tit_evap_g'] = x
    cycle_inputs['t_internal_g'] = y
    cycle_inputs['superheating'] = z
    cycle_inputs['subcooling'] = w
    return COP_Duplo_Estagio_Compress(cycle_inputs)



class particle:
    def __init__(self,position, velocity,cost,best_position,best_cost):
        self.position = position
        self.velocity = velocity
        self.cost = cost
        self.best_position = best_position
        self.best_cost = best_cost

particles = []
GlobalBestCost = 0
GlobalBestPos = 0




for i in range(0,npop):
    particles.append(particle(np.random.uniform(low= VarMin, high = VarMax, size =4),0,0,0,0))
    particles[i].cost = func1(particles[i].position[0],particles[i].position[1],particles[i].position[2],particles[i].position[3])
    particles[i].velocity = 0.01 * np.array([random.randint(-20,20),random.randint(-20,20),random.randint(-20,20),random.randint(-20,20)])
    particles[i].best_position = particles[i].position
    particles[i].best_cost = func1(particles[i].position[0],particles[i].position[1],particles[i].position[2],particles[i].position[3])
    
    
    
    
    
    for i in particles:
        if i.best_cost > GlobalBestCost:
            GlobalBestCost = i.best_cost
            GlobalBestPos = i.best_position
    
for it in range(0,maxit):
    for i in particles:
        nonnorm_velocity = w*i.velocity + c1* rand *(i.best_position - i.position)+ c2* rand *(GlobalBestPos - i.position)
        velocity_module = ((nonnorm_velocity[0]**2 + nonnorm_velocity[1]**2)**0.5)
        i.velocity = nonnorm_velocity/velocity_module
        i.position = i.position + i.velocity
        
        if i.position[0] > VarMax[0]:
            i.position[0] = VarMax[0]
        
        if i.position[0] < VarMin[0]:
            i.position[0] = VarMin[0]
        
        if i.position[1] > VarMax[1]:
            i.position[1] = VarMax[1]
        
        if i.position[1] < VarMin[1]:
            i.position[1] = VarMin[1]
            
        if i.position[2] > VarMax[2]:
            i.position[2] = VarMax[2]
        
        if i.position[2] < VarMin[2]:
            i.position[2] = VarMin[2]    
        
        if i.position[3] > VarMax[3]:
            i.position[3] = VarMax[3]
        
        if i.position[3] < VarMin[3]:
            i.position[3] = VarMin[3]
        #print(particle.position[0])
        
        i.cost = func1(i.position[0],i.position[1],i.position[2],i.position[3])
        #plt.scatter(it, i.cost, s=25)
        
        if i.cost > i.best_cost:
            i.best_cost = i.cost
            i.best_position = i.position
        
        if i.best_cost > GlobalBestCost:
            GlobalBestCost = i.best_cost
            GlobalBestPos = i.best_position
        
        
        
    
    if w > min_w:
        w = w*damp

print('Iteration', it, w)           
print('This is Global Best Cost: '+str(GlobalBestCost))
print('This is Global Best Position: '+str(GlobalBestPos))
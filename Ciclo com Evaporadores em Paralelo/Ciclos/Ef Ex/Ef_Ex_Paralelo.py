# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 14:16:33 2023

@author: Ramon
"""
import matplotlib.pyplot as plt
import numpy as np
import CoolProp as cp
from CoolProp.CoolProp import PropsSI



#Cálculo das Propriedades Termodinâmicas

def propriedades(ponto):
    variaveis=['T','P','HMASS','SMASS','Q','C']
    input_var=list(ponto.keys())
    output_var=[variable for variable in variaveis if variable not in input_var]
    outputs=PropsSI(output_var,input_var[0],ponto[input_var[0]],input_var[1],ponto[input_var[1]],ponto['refrigerant'])

    for index,variable in enumerate(output_var):
        ponto[variable]=outputs[index]
        
input_values ={
    't_external': 298,
    't_cond':308,
    't_internal_f':250,
    't_internal_g':273,
    'Q_ETB':35200, #10 TR
    'N_isent': 0.7,
    'refrigerant':'R600A',
    'subcooling':5,
    'superheating':5,
    'approach_HX':5,
    'r':1.5,
    'tit_evap_f':0.6
}

def Ef_Ex_Paralelo(cycle_inputs):
    P_ETB = PropsSI("P","T",cycle_inputs['t_internal_f'],"Q",1,cycle_inputs['refrigerant'])
    P_ETI = PropsSI("P","T",cycle_inputs['t_internal_g'],"Q",1,cycle_inputs['refrigerant'])
    
    #Pós Condensador
    point_3 = {'Q':0,'T':cycle_inputs['t_cond']-cycle_inputs['subcooling'],'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_3)
    
    
    
    #Pós HX
    point_4a = {'T':point_3['T']-cycle_inputs['approach_HX'],'P':point_3['P'],'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_4a)
    
    point_4b = {'T':point_3['T']-cycle_inputs['approach_HX'],'P':point_3['P'],'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_4b)
    
    #Evaporador da Geladeira e Disp. de Expansão 1
    point_6a = {'P':P_ETI,'T':cycle_inputs['t_internal_g'] + cycle_inputs['superheating'],'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_6a)
    print("Temp. 6a = ",point_6a['T'])
    print('Titulo 6a:',point_6a['Q'])
    
    
    
    
    point_5a = {'HMASS':point_4a['HMASS'],'P':P_ETI,'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_5a)
    print("Temp.5a = ",point_5a['T'])
    
    #VRP
    point_7a = {'HMASS':point_6a['HMASS'],'P':P_ETB,'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_7a)
    print("Temp.7a = ",point_7a['T'])
    
    
    
    #print(point_7a['Q'],point_7a['T'])
    
    #Dispositivo de Expansão 2 e Evaporador do Freezer
    
    point_5b = {'HMASS':point_4b['HMASS'],'P':P_ETB,'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_5b)
    print("temp. 5b = ",point_5b['T'])
    print("titulo 5b",point_5b['Q'])
    
    
    
    
    point_6b = {'Q':cycle_inputs['tit_evap_f'],'P':P_ETB,'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_6b)
    print("temp.6b =",point_6b['T'])
    print("titulo 6b = ",point_6b['Q'])
    
    print(point_6b['P'],P_ETB)
    
    
    #Descobrindo vazões mássicas
    
    m3 = cycle_inputs['Q_ETB']/(point_6b['HMASS']-point_5b['HMASS'])
    
    m2 = m3 * cycle_inputs['r']
    
    m1 = m2+m3
    
    print("m1, m2, m3 = ", m1,m2,m3)
    
    #Entrada do trocador
    
    h8 = (m2*point_7a['HMASS'] + m3*point_6b['HMASS'])/m1
    
    point_8 = {'HMASS':h8,'P':P_ETB,'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_8)
    print("temp. 8 = ",point_8['T'])
    
    #Compressor
    point_1 = {'P':P_ETB,'T':point_8['T']+cycle_inputs['approach_HX'],'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_1)
    print('titulo 1 =',point_1['Q'])
    
    point_2s = {'P':point_3['P'],'SMASS':point_1['SMASS'],'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_2s)
    
    
    point_2 = {'P':point_3['P'],'HMASS':point_1['HMASS'] + ((point_2s['HMASS'] - point_1['HMASS'])/cycle_inputs['N_isent']),'refrigerant':cycle_inputs['refrigerant']}
    propriedades(point_2)
    
    #Descobrindo potência da geladeira
    
    Q_ETI = m2*(point_6a['HMASS'] - point_5a['HMASS'])
    
    
    #Descobrindo potência do compressor
    
    work = m1*(point_2['HMASS'] - point_1['HMASS'])
    
    

    #Calculando taxa de destruição de exergia de cada componente
    #1. Compressor
    Sger_comp = m1*(point_2['SMASS']-point_1['SMASS'])
    Ad_comp = cycle_inputs['t_external']*Sger_comp
    print("Ad_comp",Ad_comp)
    
    #2. Condensador
    Q_cond = m1*(point_2['HMASS'] - point_3['HMASS'])
    print("Q_cond",Q_cond)
    Sger_cond = m1*(point_3['SMASS'] - point_2['SMASS']) + (Q_cond/cycle_inputs['t_external']) 
    Ad_cond = cycle_inputs['t_external'] * Sger_cond
    print("Ad_cond",Ad_cond)
    
    #3. Trocador de Calor
    Sger_HX = m1*(point_4a['SMASS'] + point_1['SMASS'] - point_8['SMASS'] - point_3['SMASS'])
    Ad_HX = cycle_inputs['t_external'] * Sger_HX
    print("Ad_HX",Ad_HX)
    
    #4. Dispositivo de Expansão 1
    Sger_DE1 = m2*(point_5a['SMASS'] - point_4a['SMASS'])
    Ad_DE1 = cycle_inputs['t_external']*Sger_DE1
    print("Ad_DE1",Ad_DE1)
    
    #5. Dispositivo de Expansão 2
    Sger_DE2 = m3*(point_5b['SMASS'] - point_4b['SMASS'])
    Ad_DE2 = cycle_inputs['t_external'] * Sger_DE2
    print("Ad_DE2",Ad_DE2)
    
    #6. Evaporador da Geladeira
    Sger_ETI = m2*(point_6a['SMASS']-point_5a['SMASS']) - (Q_ETI/point_6a['T'])
    Ad_ETI = cycle_inputs['t_external'] * Sger_ETI
    print("Ad_ETI",Ad_ETI)
    
    #7. Evaporador do Freezer
    print(point_5b['SMASS'],point_6b['SMASS'])
    Sger_ETB = m3*(point_6b['SMASS']-point_5b['SMASS']) - (cycle_inputs['Q_ETB']/point_6b['T'])
    Ad_ETB = cycle_inputs['t_external'] * Sger_ETB
    print("Ad_ETB",Ad_ETB)
    
    Ad_total = Ad_comp + Ad_cond +  Ad_DE1 + Ad_DE2 + Ad_ETI + Ad_ETB +Ad_HX
    
    ef_ex = 1 - (Ad_total/work)
    
    print(ef_ex)
    
    return ef_ex
    
    

#COP_Evap_Paralelo(input_values)    
Ef_Ex_Paralelo(input_values)
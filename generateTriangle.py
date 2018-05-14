# -*- coding: utf-8 -*-
"""
Creation_Triangle is a function to get the basic data representation of 
an actuarial triangle, showing the development of claims over time for each 
exposure (origin) period. An origin period could be the year the policy was 
written or earned, or the loss occurrence period. The development period of an 
origin period is also called age or lag. Data on the diagonals present payments
in the same calendar period. 
    
We used some methods of the ChainLadderpackage <https://github.com/mages/ChainLadder>

Parameters:
     

"""
import numpy as np
import pandas as pd
import chainladder as cl


def Creation_Triangle(IZAR, First_UWY, Run_Off_Year, Closing_Year, Seg, Risk, Pays):

    'Processing by segment code'
    AY = np.arange(First_UWY,Run_Off_Year+1)
    DY = np.arange(12,(Closing_Year-First_UWY+1)*12 + 1,12) 
    data = IZAR.loc[(IZAR.Attri_ML==Risk) & (IZAR.Code_segment==Seg)]
    if (Pays != None):
        data = data.loc[data.IBNR_Sub_Segment == Pays]
        data_groupby = data.groupby(['Annee_de_souscription','Devlopement'])
        data = data_groupby[['Paid','OS']].sum().reset_index()
    
    'Triangle of paid'
    data_Paid = data.loc[:,['Annee_de_souscription','Devlopement','Paid']].sort_values(by=['Annee_de_souscription','Devlopement'])
    tri_inc_paid = cl.Triangle(data_Paid, origin="Annee_de_souscription", dev="Devlopement", values="Paid",dataform = "triangle")
    tri_inc_paid.data_as_triangle(inplace=True)
    tri_cum_paid = tri_inc_paid.incr_to_cum(inplace=False)
     
    ' Triangle of OS : The OS must not be cumulative'
    data_OS = data[['Annee_de_souscription','Devlopement','OS']].sort_values(by=['Annee_de_souscription'])
    tri_OS = cl.Triangle(data_OS, origin="Annee_de_souscription", dev="Devlopement", values="OS", dataform ="triangle")
    tri_OS = tri_OS.data_as_triangle(inplace=True) 
    
    ' Creation of triangle incurred'
    Incurred = tri_OS + tri_cum_paid
      
    'Creation of final triangle'

    'Paid'
    Data1 = cl.Triangle(pd.DataFrame(0, index=list(AY), columns=list(DY)), origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
    Data1.update(tri_cum_paid)
    PcumTr = cl.Triangle(Data1, origin="Annee_de_souscription", dev="Devlopement" ,dataform ="triangle")
    Paid_Cum = PcumTr.data
    Paid_inc = PcumTr.cum_to_incr(inplace=False)
    
    'OS'
    Data2 = cl.Triangle(pd.DataFrame(0, index=list(AY), columns=list(DY)), origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
    Data2.update(tri_OS)
    OS = cl.Triangle(Data2, origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
      
    'Incurred'
    Data3 = cl.Triangle(pd.DataFrame(0, index=list(AY), columns=list(DY)), origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
    Data3.update(Incurred)
    Incurred = cl.Triangle(Data3, origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
    
    return (Paid_inc ,Paid_Cum, OS, Incurred) 



IZAR = pd.read_csv("IZAR_Input_ResQ_Paid.txt", sep= '\t', decimal=",")
First_UWY = 1963
Run_Off_Year = 2006
Closing_Year = 2015
Seg = "2GL2"
Risk = "Attri"
Pays = None


(Paid_inc ,Paid_Cum, OS, Incurred)  = Creation_Triangle(IZAR, First_UWY, Run_Off_Year, Closing_Year, Seg, Risk, Pays)
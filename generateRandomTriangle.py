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


def Creation_Random_Triangle(IZAR, First_UWY, Run_Off_Year, begin_date, end_date, Seg, Risk, Pays, first_dev, len_dev, val_dev):
    # Ingredients
    AY = np.arange(First_UWY,Run_Off_Year+1)
    DY = np.arange(len_dev,(Closing_Year-First_UWY+1)*len_dev + 1,len_dev) 
    year_list = np.arange(begin_date, end_date+1)
    ctr = 0 
    df = pd.DataFrame(index =np.arange(len(year_list)*(val_dev+1)) ,columns=["Annee_de_souscription","Devlopement","Paid","OS"] )
    devList = []
    yearSousList = []
    # Substruct statistical parameters from IZAR
    data = IZAR.loc[(IZAR.Attri_ML==Risk) & (IZAR.Code_segment==Seg)]
    if (Pays != None):
        data = data.loc[data.IBNR_Sub_Segment == Pays]
    data_groupby = data.groupby(['Annee_de_souscription','Devlopement'])
    data = data_groupby[['Paid','OS']].sum().reset_index()

    # Filling IZAR table
    for i in year_list:
        devList = np.append(devList,np.arange(first_dev+ctr,first_dev+(len_dev*val_dev)+ctr+1,len_dev).T)
        yearSousList = np.append(yearSousList,np.array([i for j in range(val_dev+1)]).T)
        ctr -= val_dev
        df.Devlopement = pd.Series(devList)
    df.Annee_de_souscription= pd.Series(yearSousList)
    df.Paid = np.random.normal(data.Paid.mean(), data.Paid.std(), df.Annee_de_souscription.shape[0])
    df.OS = np.random.normal(data.OS.mean(), data.OS.std(), df.Annee_de_souscription.shape[0])
    df.Annee_de_souscription = df.Annee_de_souscription.astype(int)
    df.Devlopement = df.Devlopement.astype(int)
    
    # Substructing triangles
    'Triangle des paid'
    df_data_Paid = df.loc[:,['Annee_de_souscription','Devlopement','Paid']].sort_values(by=['Annee_de_souscription','Devlopement'])
    df_inc_paid = cl.Triangle(df_data_Paid, origin="Annee_de_souscription", dev="Devlopement", values="Paid",dataform = "triangle")
    df_inc_paid.data_as_triangle(inplace=True)
    df_cum_paid = df_inc_paid.incr_to_cum(inplace=False)

    'Triangle des OS : Les OS ne doivent pas être cumules'
    df_data_OS = df.loc[:,['Annee_de_souscription','Devlopement','OS']].sort_values(by=['Annee_de_souscription','Devlopement'])
    df_OS = cl.Triangle(df_data_OS, origin="Annee_de_souscription", dev="Devlopement", values="OS", dataform ="triangle")
    df_OS = df_OS.data_as_triangle(inplace=True) 

    'Creation du triangle incurred'
    df_Incurred = df_OS + df_cum_paid
    'Creation du triangle final'
    'Paid'
    df_Data1 = cl.Triangle(pd.DataFrame(0, index=list(AY), columns=list(DY)), origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
    df_Data1.update(df_cum_paid)
    df_PcumTr = cl.Triangle(df_Data1, origin="Annee_de_souscription", dev="Devlopement" ,dataform ="triangle")
    df_Paid_Cum = df_PcumTr.data
    df_Paid_inc = df_PcumTr.cum_to_incr(inplace=False)
    'OS'
    df_Data2 = cl.Triangle(pd.DataFrame(0, index=list(AY), columns=list(DY)), origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
    df_Data2.update(df_OS)
    df_OS = cl.Triangle(df_Data2, origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data

    'Incurred'
    df_Data3 = cl.Triangle(pd.DataFrame(0, index=list(AY), columns=list(DY)), origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
    df_Data3.update(df_Incurred)
    df_Incurred = cl.Triangle(df_Data3, origin="Annee_de_souscription", dev="Devlopement", dataform ="triangle").data
    return (df_Paid_inc ,df_Paid_Cum, df_OS, df_Incurred) 



IZAR = pd.read_csv("IZAR_Input_ResQ_Paid.txt", sep= '\t', decimal=",")
First_UWY = 1963
Run_Off_Year = 2006
Seg = "2GL2"
Risk = "Attri"
Pays = None
Closing_Year = 2015
first_dev = 300 # First development in the first year / must first_dev > val_dev*len(year_list)
len_dev = 10 # gap between each development in a year
val_dev = len_dev # number of development by year
begin_date = 1977
end_date = 2003



(Paid_inc ,Paid_Cum, OS, Incurred)  = Creation_Random_Triangle(IZAR, First_UWY, Run_Off_Year, begin_date, end_date, Seg, Risk, Pays, first_dev, len_dev, val_dev)
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 16:33:52 2022

@author: jakub.kucera
"""

import win32com.client.dynamic
import numpy as np

import PySimpleGUI as sg

def ShowSplines(lf):
    #Takes a layup file and generates splines and points in CATIA
    #CATIA start
    CATIA = win32com.client.Dispatch("CATIA.Application")
    partDocument2 = CATIA.ActiveDocument
    part1 = partDocument2.Part
    HSF = part1.HybridShapeFactory
    #originElements1 = part1.OriginElements
    hbs = part1.HybridBodies
    
    # Adding new body to part1
    body2 = hbs.Add()
    # Naming new body as "wireframe"
    body2.Name="gs2"
    
    # Adding new body to part1
    body1 = hbs.Add()
    # Naming new body as "wireframe"
    body1.Name="pts2"

    #read the file
    with open(lf, "r") as text_file:
        f = text_file.read()
        
    w = f.split("[LAMINATE]")[1]
    w = w.split("[SPLINES]")[0]
    spls = w.split('\n')[2]
    #print(spls)
    
    #unique splines list
    unique = []
    spls = spls.replace("[","")
    spls = spls.replace("]","")
    spls = spls.replace("'","")
    for x in spls.split(",")[:]:
       if x not in unique:
           x = x.replace(" ","")
           unique.append(x)
    
    f = f.split("[SPLINES]")[1]
    for spl in unique:
        spl2 = spl.replace("'","")
        if spl2 == 'f':
            #edge spline is closed always
            spl2 = "[EDGE SPLINE]"
            fx = f.split(spl2+"\n")[1]
        else:
            fx = f.split(spl2)[1]
            print(fx)
            fx = fx.split("spline\n")[1]
        
        
        #for each spline
        #while loop for each spline
        hss1 = HSF.AddNewSpline()
        hss1.SetSplineType(0)
        hss1.SetClosing(1)
        
        #might need more splines for one line
        #  - in such case join will be requied, points will need 4th datapoint T/F
        #  - this will allow for sharp corners
        
        for xw in fx.split("\n")[:]:
            if xw == "":
                #empty lines ends the for-loop for current spline
                break
            else:
                #take x,y,z coordinates from each line
                x = xw.split()[0]
                y = xw.split()[1]
                z = xw.split()[2]
                cord1 = HSF.AddNewPointCoord(x, y, z)
                body1.AppendHybridShape(cord1)
                ref2 = part1.CreateReferenceFromObject(cord1)
                hss1.AddPointWithConstraintExplicit(ref2,None,-1,1,None,0)

        body2.AppendHybridShape(hss1)
        hss1.Name=spl2
        part1.Update
    
    #hide the point set
    selection1 = partDocument2.Selection
    visPropertySet1 = selection1.VisProperties
    selection1.Add(body1)
    visPropertySet1 = visPropertySet1.Parent
    visPropertySet1.SetShow(1)
    selection1.Clear 
    part1.Update


    print("splines uploaded to current CATIA part")
    
#very simple UI section:        
s2 = 35
s1 = 25
layout2 = [[sg.FilesBrowse('Layup file:',size=(int(s2/3),1)),sg.Text("",key='lf',size=(s1,1)),],
           [sg.Button('Import', key='b',size=(15,1))]]

window = sg.Window('Layup Definition', layout2, default_element_size=(12,1),size=(300,80))

print("loading UI...")

#GUI function loop
while True: 
    #read all potential user inputs
    event, values = window.read()    
    
    if event is None: # way out!    
        break  
    
    if event in 'b':
        if values['Layup file:'] == "":
            print("please specify layup file")
        else:
            ShowSplines(values['Layup file:'])
            
            
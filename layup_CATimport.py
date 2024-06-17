# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 16:33:52 2022

@author: jakub.kucera
"""

import win32com.client.dynamic
import numpy as np

from jsonic import serialize, deserialize

#import PySimpleGUI as sg

def ShowSplines(D):
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

    import stcOBJ


    for i,spl in enumerate(D.allGeometry):
        #print(spl)

        #print(type(spl))
        if type(spl) == stcOBJ.Spline:
            
          
            #for each spline
            #while loop for each spline
            hss1 = HSF.AddNewSpline()
            hss1.SetSplineType(0)
            hss1.SetClosing(1)
            
            #might need more splines for one line
            #  - in such case join will be requied, points will need 4th datapoint T/F
            #  - this will allow for sharp corners
            
            for ii,pt in enumerate(spl.points):
                
                #take x,y,z coordinates from each line
                cord1 = HSF.AddNewPointCoord(pt.x, pt.y, pt.z)
                body1.AppendHybridShape(cord1)
                ref2 = part1.CreateReferenceFromObject(cord1)
                hss1.AddPointWithConstraintExplicit(ref2,None,-1,1,None,0)

            body2.AppendHybridShape(hss1)
            hss1.Name="spline_ID_"+str(i)+"_"+spl.memberName
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


#no UI for import in this version

file = "D:\\CAD_library_sampling\\TestCad_SmartDFM\\X\\x_test_131_layup.json"

#open file
with open(file,"r") as in_file:
    json_str= in_file.read()

#print(json_str)

D = deserialize(json_str,string_input=True)

ShowSplines(D)
    

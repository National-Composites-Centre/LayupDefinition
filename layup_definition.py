# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:34:14 2022

@author: jakub.kucera
"""
import win32com.client.dynamic
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize) #for troubleshooting only
from vecEX3 import wrmmm
import PySimpleGUI as sg
import os
from datetime import date
import math

from secondary_UIs import newMat #currently unused cleanup - because of parameter passing issues between UI's in differnt scripts
from utilities import sharpness

version = "4.0"

def pts100(sp,hbs,hs,part1,HSF,partDocument2,dir = False,no_p = 100):
    # Adding new body to part1
    body1 = hbs.Add()
    # Naming new body as "wireframe"
    body1.Name="ref"+str(sp)
    
    # Adding new body to part1
    body2 = hbs.Add()
    # Naming new body as "wireframe"
    body2.Name="output"+str(sp)
    hpo1 = hs.Item(str(sp))
    ref1 = part1.CreateReferenceFromObject(hpo1)
    
    #reference point on default - does not need to be on part
    point=HSF.AddNewPointCoord(0,0,0)
    body1.AppendHybridShape(point) 
    point.Name="p1"
    ref2 = part1.CreateReferenceFromObject(point)
    selection1 = partDocument2.Selection
    visPropertySet1 = selection1.VisProperties
    selection1.Add(point)
    visPropertySet1 = visPropertySet1.Parent
    visPropertySet1.SetShow(1)
    
    #iterate to add 100 equidistant points on the spline - irrespective of lenght
    i = 0
    while i < no_p:
        hpc1 = HSF.AddNewPointOnCurveWithReferenceFromPercent(ref1, ref2, i/no_p, dir)
        body2.AppendHybridShape(hpc1)
        i = i + 1
        
    part1.Update()
    #export .wrl with only the latest spline points visible
    partDocument2.ExportData("C:\\temp\\xxx.wrl", "wrl")
    #standard .wrl interogation to obtain point locations
    vec, x = wrmmm(Multi = True)
    #corrects for extra 0,0,0 point
    #x = np.delete(x,0,axis=0)

    return(x,body1,body2)

def SplinesToClouds(spNames,no_p = 100,CADfile=""):
    #Support function that generates a cloud of points (approx. equidistant) 
    #from a spline selected.
    
    #number of points per spline: no_p

    #CATIA basic initiation
    CATIA = win32com.client.Dispatch("CATIA.Application")
    partDocument2 = CATIA.ActiveDocument
    part1 = partDocument2.Part
    HSF = part1.HybridShapeFactory
    originElements1 = part1.OriginElements
    hbs = part1.HybridBodies
    
    #requires standard splines geo. set definition
    hb = hbs.Item("gs2")
    hs = hb.HybridShapes
    
    mat_list = []
    #lists True/False values for each spline close status
    closed_list = []
    for sp in spNames:
        
        x,body1, body2= pts100(sp,hbs,hs,part1,HSF,partDocument2,no_p=no_p)

        #cover for wrong direction in non-continous spline
        if ((x[0,0]-x[1,0] == 0)
            and (x[0,1]-x[1,1] == 0)
            and (x[0,2]-x[1,2] == 0)):
            #iterate to add 100 equidistant points on the spline - irrespective of lenght
            
            selection1 = partDocument2.Selection
            selection1.Clear()
            selection1.Add(body1)
            selection1.Add(body2)
            selection1.Delete() 

            x,body1,body2 = pts100(sp,hbs,hs,part1,HSF,partDocument2,dir=True,no_p = no_p)

        #now figure out if spline is closed
        tdist = math.sqrt((x[0,0]-x[98,0])**2+(x[0,1]-x[98,1])**2+(x[0,2]-x[98,2])**2)
        #print(tdist)
        if tdist < 12: #arbitrary 5mm treshold
            sp_closed = "closed spline"
        else:
            sp_closed = "open spline"
        
        #hide the geometry that was already exported - avoids polluting any further exports - hides the point and normal specifically
        selection1 = partDocument2.Selection
        visPropertySet1 = selection1.VisProperties
        selection1.Add(body1)
        visPropertySet1 = visPropertySet1.Parent
        visPropertySet1.SetShow(1)
        selection1.Add(body2)
        visPropertySet1 = visPropertySet1.Parent
        visPropertySet1.SetShow(1)
        selection1.Clear 
        mat_list.append(x)
        closed_list.append(sp_closed)
        
    #this might be removed later: (either remove or improve notations)
    #obtain the spline points for the overall edge:
    try:
        hybridBody1 = hbs.Item("main_shape")
        hybridShapes1 = hybridBody1.HybridShapes
        hybridShapeSplit1 = hybridShapes1.Item("MainS")
        reference1 = part1.CreateReferenceFromObject(hybridShapeSplit1)
        hybridShapeBoundary1 = HSF.AddNewBoundaryOfSurface(reference1)
    except:
        sg.Popup("Please make sure geometric set called 'main_shape' exits,"
                 +" and contains only main layup surface (tool), called 'MainS'",keep_on_top=True)
        #hopefully should close spline editing, but not the GUI?
        #error = True
        return(mat_list,[0,0,0],False)

    #The above is repeated for edge spline - created by boundary function 
    #in CATIA. There might be a better way to do this, than repeating code...

    #Adding new body to part1
    body2 = hbs.Add()
    # Naming new body as "wireframe"
    body2.Name="output_edge"

    body2.AppendHybridShape(hybridShapeBoundary1)

    #part1.InWorkObject = hybridShapeBoundary1

    #part1.Update 
    point=HSF.AddNewPointCoord(0,0,0)
    body2.AppendHybridShape(point) 
    point.Name="px"
    ref3 = part1.CreateReferenceFromObject(point)

    ref2 = part1.CreateReferenceFromObject(hybridShapeBoundary1)

    #hybridBody3 = hbs.Item("gs2")

    hybridShapeNear1 = HSF.AddNewNear(ref2, ref3)
    ref66 = part1.CreateReferenceFromObject(hybridShapeNear1)

    body2.AppendHybridShape(hybridShapeNear1)

    selection1 = partDocument2.Selection
    visPropertySet1 = selection1.VisProperties
    selection1.Add(body2)
    visPropertySet1 = visPropertySet1.Parent
    visPropertySet1.SetShow(1)

    # Adding new body to part1
    body1 = hbs.Add()
    # Naming new body as "wireframe"
    body1.Name="edge_points"

    i = 0
    while i < no_p:
        hpc1 = HSF.AddNewPointOnCurveWithReferenceFromPercent(ref66, ref3, i/no_p, False)
        body1.AppendHybridShape(hpc1)
        i = i + 1
            
    part1.Update()
    partDocument2.ExportData("C:\\temp\\xxx.wrl", "wrl")
    vec, edge_points = wrmmm(Multi = True)

    edge_points = np.delete(edge_points,0,axis=0)
    
    #hide the geometry that was already exported - avoids polluting any further exports - hides the point and normal specifically
    selection1 = partDocument2.Selection
    visPropertySet1 = selection1.VisProperties
    selection1.Add(body1)
    visPropertySet1 = visPropertySet1.Parent
    visPropertySet1.SetShow(1)

    #list of splines-point-lists, and edge points exported separately
    return(mat_list,edge_points,True,closed_list)

# THIS IS NEW "LF3" HAS TO BE REPLACED , BUT ALSO
# 1. INITIAL COMBO BOX IS []
# 2. ONCE LOCATION OF FOLDER HAS BEEN ADDED (ON EVENT), RUN THIS AND UPDATE COMBO BOX WITH SEZNAM

# 3. THEN ALSO ADDRESS THE BIT OF CODE WHICH DEALS WITH STORING NEW VALUES INTO THE FILE 

seznam2 = ["","uniform","variable"]

#GUI definition 
#Eventually make the number of input drop-offs flexible.
#Consider making the overall layup box bigger, or easier to edit...
s2 = 35
s1 = 25
s3 = 15
s4 = 10
s5 = 20

#repeated size of UI - for easer adjusting 
sX = [35,25,15,10,20]

no_p = 100

#original reference for stacking direction
x_ref = ""
y_ref = ""
z_ref = ""
x_dir = ""
y_dir = ""
z_dir = ""
str_sd = ""

try: 
    CATIA = win32com.client.Dispatch("CATIA.Application")
    partDocument2 = CATIA.ActiveDocument
    cat_name = CATIA.ActiveDocument.Name
    cat_name = cat_name.split(".CATPart")[0]
except:
    cat_name = ""
    
def_folder = "C:\\teemp\\"
#sg.Text('Location:',size=(s1,1)),sg.InputText("C:\\teemp\\", key='location',size=(s2, 1))],

#dictionary for tooltips
tooltipDict = {"LD_create": 'This button generates the "layup definition" according to all information above.', 
        "nm": 'The layup file name should be the same as the CATIA part name. (without the extension)', 
        "loc": 'The working directory should have material database file and CATIA part in it.\nThis will also'
            +' be the location of LD .txt file.',
        "ol": 'This should include all layers, no matter the locations of drop-offs.\n'
            +'Do include the square brackets in the field.\n'
            +'The layers should be listed starting from the tool face.',
        'mm':'Select if only one material is used (uniform). Or different materials are present in the layup (variable).\n'
            +'If variable material option was selected fill in each line appropriately in the pop-up window.\n'
            +'Do not edit the single drop-down on the main window, if list of materials have been provided individually.\n'
            +'To re-open the pop-up re-select the "variable" option in the left combo-box.\n'
            +'If new material is required, use the "Add new material buttion"',
        'sp1':'On its own "Spline 1" is used as a single ply drop-off.\n'
            +'It is recommended that splines are closed, but open splines should also work most of the time,\n'
            +'as long as these fully split the surface. All splines must be fully in contact with main surface.\n'
            +'The spline can be any curve-like geometry. It needs to be placed in "gs2" geometrical set.\n'
            +'The numbers in the 3rd column correspond to plies dropped at that location (delimited by ",").\n'
            +'The index numbers correspond to order of listed plies above.\n',
        'sp2':'"Spline 2" is used to turn single spline definition of drop-off, to zone containing multiple drop-offs.\n'
            +'These drop-offs will be automatically spaced between the two splines.\n'
            +'(This functionality is in early stages of testing)'
            }

layout2 = [[sg.Text('Layup file name:',tooltip = tooltipDict["nm"],size=(s3,1)),sg.InputText(cat_name, key='name',size=(s3, 1))],
           [sg.Text("Location:",tooltip = tooltipDict["loc"],size=(s3,1)), sg.Input(key='location',size=(int(s3))),sg.FolderBrowse("Select",size=(int(s2/3),1))],
           [sg.Text('Layup in follwoing format below:',size=(int(s1),1)),sg.T("[0,90,-45,45]",size=(int(s2),None))],
           [sg.Text('Overall layup',tooltip = tooltipDict["ol"], size=(s1, 1)), sg.InputText("", key='lup',size=(s2, 1))], 
           [sg.Text('Material',tooltip = tooltipDict["mm"], size=(s3,1)),sg.Combo(seznam2,size=(s3,1),key='klic16',enable_events=True),sg.Combo([],size=(s3,1),disabled=True,key='klic')],  
           #mixed materials option to be added...
           #[sg.Text('Insert limits for specific layers, index based on order above starting with 1:',size=(s1+s2,1))], -- this needs to be provided as advice
           [sg.Button('Selecting stacking direction (optional):',key="s_dir",size=(s2,1)),sg.Checkbox("", False, key="sd_check",disabled=True),],
           [sg.Button('Spline 1 - interactive',tooltip = tooltipDict["sp1"], key='spl',size=(s1,1)),sg.Button('Spline 2 - interactive',tooltip = tooltipDict["sp2"],key='sp2',size=(s1,1)),],
           [sg.Button('Add new material', key='matN',size=(s1,1)),],
           [sg.Text("spline 1",size=(s5,None)),sg.T("spline 2 (optional)",size=(s5,None)),sg.T("1,4",size=(s2,None))],
           [sg.InputText("", key='1t',size=(s5, 1)),sg.InputText("", key='1s',size=(s5, 1)), sg.InputText("", key='1v',size=(s2, 1))], 
           [sg.InputText("", key='2t',size=(s5, 1)),sg.InputText("", key='2s',size=(s5, 1)), sg.InputText("", key='2v',size=(s2, 1))],
           [sg.InputText("", key='3t',size=(s5, 1)),sg.InputText("", key='3s',size=(s5, 1)), sg.InputText("", key='3v',size=(s2, 1))],
           [sg.InputText("", key='4t',size=(s5, 1)),sg.InputText("", key='4s',size=(s5, 1)), sg.InputText("", key='4v',size=(s2, 1))],
           [sg.InputText("", key='5t',size=(s5, 1)),sg.InputText("", key='5s',size=(s5, 1)), sg.InputText("", key='5v',size=(s2, 1))],
           [sg.InputText("", key='6t',size=(s5, 1)),sg.InputText("", key='6s',size=(s5, 1)), sg.InputText("", key='6v',size=(s2, 1))],
           [sg.InputText("", key='7t',size=(s5, 1)),sg.InputText("", key='7s',size=(s5, 1)), sg.InputText("", key='7v',size=(s2, 1))],
           [sg.InputText("", key='8t',size=(s5, 1)),sg.InputText("", key='8s',size=(s5, 1)), sg.InputText("", key='8v',size=(s2, 1))],
           [sg.InputText("", key='9t',size=(s5, 1)),sg.InputText("", key='9s',size=(s5, 1)), sg.InputText("", key='9v',size=(s2, 1))],
           [sg.InputText("", key='10t',size=(s5, 1)),sg.InputText("", key='10s',size=(s5, 1)), sg.InputText("", key='10v',size=(s2, 1))],
           [sg.Button('Create layup file',key='clf',tooltip = tooltipDict["LD_create"],size=(15,1))]]
           #[sg.InputText("", key='11t',size=(s1, 1)), sg.InputText("", key='11v',size=(s2, 1))], 
           #[sg.InputText("", key='12t',size=(s1, 1)), sg.InputText("", key='12v',size=(s2, 1))],
           #[sg.InputText("", key='13t',size=(s1, 1)), sg.InputText("", key='13v',size=(s2, 1))],
           #[sg.InputText("", key='19t',size=(s1, 1)), sg.InputText("", key='19v',size=(s2, 1))],
           #[sg.InputText("", key='20t',size=(s1, 1)), sg.InputText("", key='20v',size=(s2, 1))]]

window = sg.Window('Layup Definition '+version, layout2, default_element_size=(12,1),size=(400,560),keep_on_top=True)

print("loading UI...")
#GUI function loop
while True: 
    #read all potential user inputs
    event, values = window.read()    
    
    if event is None: # way out!    
        break  


    if event in 'klic16':
        #if values['klic16'] == "uniform":
        
        lf3 = values['location']+"/"+"LD_layup_database.txt"
        try:
            with open(lf3, "r") as text_file:
                seznam = []
                for i ,line in enumerate(text_file.readlines()):
                    if line.count(",") > 0 and i != 0:
                        #print("yes")
                        m_ref = line.split(",")[1]
                        seznam.append(m_ref)
        
        except:
            sg.Popup("Material database file was not found in the location specified.\n"
                    +"Therefore an empty materil file has been created, but needs to be populated.")
            with open(lf3, 'w') as f:
                f.write("id,Material_name,	E1,	E2,	G12, G23,	v12,"
                        +"	Info_source,	layer_thickness,	density,	perme_coeff, type")
            seznam = []

        #print(seznam)

        window.Element('klic').Update(values = seznam)
        window.Element('klic').Update(disabled=False)

        if values['klic16'] == "variable":

            #if layup empty 
            if values['lup'] == "":
                wn = sg.Popup("please specify layup sequence first",keep_on_top=True)

            else:
                #obtain layup
                ll = values['lup']
                ll = ll.replace("[","")
                ll = ll.replace("]","")
                l_list = []
                cnt = ll.count(",")
                i = 0
                while i < cnt+1:
                    l_list.append(ll.split(",")[i])
                    i = i + 1
                #create layout 3 through string addition
                build = """c1 = [[sg.Text('Enter corresponding materials:',size=(40,1))]"""
                for i, a in enumerate(l_list):
                    build = build + """,[sg.Text('"""+str(a)+"""',size=(4,1)), sg.Combo(seznam,size=(17,1),key='"""+str(i)+"""k')]"""
                build = build + """,[sg.Button('Save',key='button_X',size=(10,1))]"""
                build = build + "]"
                #execute to launch layuout 3 with x combo boxes 
                exec(build)

                layout3 = [
                [
                sg.Column(c1, scrollable=True,  vertical_scroll_only=True,size=(280,280)) #,size_subsample_height=1)
                ]
                ]

                window2 = sg.Window('Material list', layout3, default_element_size=(12,1),size=(280,280),keep_on_top=True)
                #GUI function loop
                while True: 
                    #read all potential user inputs
                    event2, values2 = window2.read()    
                    
                    if event2 is None: # way out!    
                        break  
                    if event2 in 'button_X':
                        #once ok clicked store the list of materials 
                        i = 0 
                        str_ml = ""
                        while i < cnt+1:
                            str_ml += values2[str(i)+'k']
                            i = i + 1
                            if i != cnt+1:
                                str_ml +=","

                        #print(str_ml)
                        window2.close()

                        #print list of materials in the disabled combo box on the right
                        window.Element('klic').Update(value=str_ml)

            #[dont forget to edit below -- instead of uniform have option for variable or none, and list of materials]

        #elif values['klic16'] == "test":
        #    #secret way of developer testing the UI 
        #    from testing import testUI
        #
        #    testUI()
    if event in "s_dir":
        #stacking direction definition

        seznam6 = ["enter values manually", "select point and line interactively"]

        layout66 = [[sg.Combo(seznam6,size=(s2,1),key='klic66',enable_events=True)],
        [sg.Text('Refernce point:',size=(s1,1))],
        [sg.Text('x:',size=(s4,1)),sg.InputText(x_ref, key='x_ref',disabled=True,size=(s4, 1))],
        [sg.Text('y:',size=(s4,1)),sg.InputText(y_ref, key='y_ref',disabled=True,size=(s4, 1))],
        [sg.Text('z:',size=(s4,1)),sg.InputText(z_ref, key='z_ref',disabled=True,size=(s4, 1))],
        [sg.Text('Refernce direction:',size=(s1,1))],
        [sg.Text('dir. x:',size=(s4,1)),sg.InputText(x_dir, key='x_dir',disabled=True,size=(s4, 1))],
        [sg.Text('dir. y:',size=(s4,1)),sg.InputText(y_dir, key='y_dir',disabled=True,size=(s4, 1))],
        [sg.Text('dir. z:',size=(s4,1)),sg.InputText(z_dir, key='z_dir',disabled=True,size=(s4, 1))],
        [sg.Button('Save stacking direction',key='std',size=(s2,1))]]

        window66 = sg.Window('Stacking direction definition', layout66, default_element_size=(12,1),size=(250,330),keep_on_top=True)

        while True: 
            #read all potential user inputs
            event66, values66 = window66.read()    
            
            if event66 is None: # way out!    
                break  
            if event66 in 'klic66':
                
                if values66['klic66'] == "enter values manually":
                    window66.Element('x_ref').Update(disabled=False)
                    window66.Element('y_ref').Update(disabled=False)
                    window66.Element('z_ref').Update(disabled=False)
                    window66.Element('x_dir').Update(disabled=False)
                    window66.Element('y_dir').Update(disabled=False)
                    window66.Element('z_dir').Update(disabled=False)

                elif values66['klic66'] == "select point and line interactively":

                    sg.Popup("Interactive option currently not available. Please selec manual entry option.",keep_on_top=True)

            if event66 in 'std':
                #check if all 6 fields are filled
                if (values66['x_ref'] != "")\
                    and (values66['y_ref'] != "") \
                    and (values66['z_ref'] != "") \
                    and (values66['x_dir'] != "") \
                    and (values66['y_dir'] != "") \
                    and (values66['z_dir'] != "") :

                    try:
                        x_ref = float(values66['x_ref'])
                        y_ref = float(values66['y_ref'])
                        z_ref = float(values66['z_ref'])
                        x_dir = float(values66['x_dir'])
                        y_dir = float(values66['y_dir'])
                        z_dir = float(values66['z_dir'])

                        str_sd = "\n[STACKING DIRECTION]\n"
                        str_sd += "["+str(x_ref)+","+str(y_ref)+","+str(z_ref)+"]"+"\n"
                        str_sd += "["+str(x_dir)+","+str(y_dir)+","+str(z_dir)+"]"+"\n"
                    
                        window66.close()

                        #mark checkbox in main window
                        window.Element('sd_check').Update(True,checkbox_color="green")
                        #sg.Checkbox("", False, key="sd_check",disabled=True)
                    except:
                        sg.Popup("the 6 inputs must be numbers",keep_on_top=True)
                else:
                    sg.Popup("All 6 fields must be filled!",keep_on_top=True)

    if event in 'spl':
        #Initiate CATIA interaction
        CATIA = win32com.client.dynamic.DumbDispatch('CATIA.Application')
        c_doc = CATIA.ActiveDocument
        c_sel = c_doc.Selection
        c_prod   = c_doc.Product
        
        # New part where the feature should be pasted
        #new_prod = c_prod.Products.AddNewComponent("Part", "")
        #new_part_doc = new_prod.ReferenceProduct.Parent
        
        #from user selection
        try:
            sel_obj = c_sel.Item(1).Value.Name
            i = 1
            while i < 11:
                if values[str(i)+"t"]=="":
                    window.Element(str(i)+'t').Update(value=sel_obj)
                    break
                i = i + 1
                if i == 11:
                    print("currently only 10 splines are supported")
        except:

            wn = sg.Popup("please select an object first",keep_on_top=True, auto_close_duration=30)
            
    if event in 'sp2':
        
        #Initiate CATIA interaction
        CATIA = win32com.client.dynamic.DumbDispatch('CATIA.Application')
        c_doc = CATIA.ActiveDocument
        c_sel = c_doc.Selection
        c_prod   = c_doc.Product
        
        # New part where the feature should be pasted
        #new_prod = c_prod.Products.AddNewComponent("Part", "")
        #new_part_doc = new_prod.ReferenceProduct.Parent
        
        #from user selection
        try:
            sel_obj = c_sel.Item(1).Value.Name
            i = 1
            while i < 11:
                if values[str(i)+"s"]=="":
                    window.Element(str(i)+'s').Update(value=sel_obj)
                    break
                i = i + 1
                if i == 11:
                    wn = sg.Popup("currently only 10 splines are supported",keep_on_top=True, auto_close_duration=30) 
        except:

            wn = sg.Popup("please select an object first",keep_on_top=True, auto_close_duration=30)    
    
    if event in 'clf':
        #Upon running the layup generation
        i = 1
        #spline list
        spls = []
        while i < 11:
            if values[str(i)+"t"] != "":
                spls.append(values[str(i)+"t"])
            i = i + 1

        i = 1
        while i < 11:
            if values[str(i)+"s"] != "":
                spls.append(values[str(i)+"s"])
            i = i + 1
        
        CADfile = values["location"]+"/"+values["name"]+".txt"
        #create points delimiting layers
        mat_list, edge_points,rrun,close_list = SplinesToClouds(spls,CADfile=CADfile)

        #add column defining spline interuptions (i.e. corners)
        i = 0
        while i < len(mat_list):
            #for all defined splines
            mat_list[i] = sharpness(mat_list[i])
            i = i + 1

        #for edge points - corners
        edge_points = sharpness(edge_points)
        
        if rrun == True:
        
            #start constructing the layup .txt file
            str_def = "[INFO] \n"
            str_def += "generated using Python tool version "+version+" \n"
            str_def += "author: " + str(os.getlogin()) +"\n"

            #basic info / header
            today = date.today()
            d1 = today.strftime("%d/%m/%Y")    
            str_def += "generated on: " + str(d1)+ "\n \n \n "
            
            #cad reference file
            str_def += "[PART] \n"
            str_def += CADfile +"\n \n"
            #the layup itself
            str_def += "[LAMINATE] \n"
            str_def += str(values["lup"])+"\n"
            
            #preparing to loop through layers, to define drop-offs
            lam = values["lup"]
            cnt_l = lam.count(",")+1
            
            #on default all drop-off denoted as "f", full surface used
            i = 0
            sp_ref = []
            while i < cnt_l:
                sp_ref.append("f")
                i = i + 1
            
            i = 1
            error = False
            transitional_splines = False
            assigned = []
            while i < 11:
                if values[str(i)+"v"] != "":
                    
                    tv = values[str(i)+"v"] 
                    ii = 0
                    cnt = tv.count(",")
                    while ii < cnt+1:
                        tvx = int(tv.split(",")[ii])
                        
                        loc_sp = values[str(i)+"t"]
                        #checking the layer number fits within the total layup listed
                        if tvx > cnt_l:
                            sg.Popup("layer "+str(tvx)+" is not listed above. Please adjust your definition.",keep_on_top=True)
                            error = True
                        else:
                            #check that no layer is dropped-off twice
                            if tvx in assigned:
                                sg.Popup("layer "+str(tvx)+" is assigned to multiple limits. Please adjust your definition.",keep_on_top=True)
                                error = True
                            else:
                                if values[str(i)+"s"] == "":
                                    sp_ref[tvx-1] = loc_sp
                                    assigned.append(tvx)
                                else:
                                    #this else exists for the purposes of 2-spline delimitation

                                    #the below replaces spline by composite spline name
                                    #this name will required additional spline creation based on this 
                                    sp_ref[tvx-1] = loc_sp+"+++"+values[str(i)+"s"]+"+++"+str(tvx)
                                    assigned.append(tvx)
                                    #to get additional splines later
                                    transitional_splines = True
                        ii = ii + 1
                i = i + 1

            #below if function exists for the purposes of 2-spline delimitation
            #different mechanism might need to be considered - large layup-files will come of this!
            if transitional_splines == True:
                done = []
                for s in sp_ref:
                    #if composite spline
                    if ("+++" in s) and (s not in done):
                        #find the releveant splines and points
                        for i, s2 in enumerate(spls):
                            if s2 == s.split("+++")[0]:
                                sp1 = s2
                                pts1 = mat_list[i]
                                cls1 = close_list[i]
                                
                        for ii, s3 in enumerate(spls):
                            if s3 == s.split("+++")[1]:
                                sp2 = s3
                                pts2 = mat_list[ii]
                                cls2 = close_list[ii]
                                
                        #find nearest points to each other
                        mind = 99999999
                        for i, p1 in enumerate(pts1[:,0]):
                            for ii, p2 in enumerate(pts2[:,0]):
                                d = math.sqrt((pts1[i,0]-pts2[ii,0])**2+(pts1[i,1]-pts2[ii,1])**2+(pts1[i,2]-pts2[ii,2])**2)
                                if d < mind:
                                    mind = d
                                    p1_ref = i
                                    p2_ref = ii

                        #TO RESOLVE:
                        #here also check that splines go in the same circular direction  (by nearest next point...)

                        #how many times this combination of splines
                        cnt = []
                        for s2 in sp_ref:
                            if "+++" in s2:
                                if (s.split("+++")[1] == s2.split("+++")[1]) and (s.split("+++")[0] == s2.split("+++")[0]):
                                    #careful, what if the order of reference changes?
                                    cnt.append(s2)

                        #prep empty matrices
                        l_sp = []
                        for c in cnt:
                            l_sp.append(np.asarray([[0,0,0,0]]))

                        #check splines are same type closed/open or break generation
                        if cls1 != cls2:
                            sg.Popup("To splines specified for delimitation, but one is closed and one open spline.",keep_on_top=True)
                            error = True
                            break
                            
                        iii = 0
                        i = p1_ref
                        ii = p2_ref

                        #go throgh all points and collect intermediate points for the spline in question
                        while iii < no_p:
                            #if splines have diffferent sizes one, point cloud will trail behind the other
                            #This minimizes the issue by skipping points when next one creates shorter link
                            d_main = math.sqrt((pts1[i,0]-pts2[ii,0])**2+(pts1[i,1]-pts2[ii,1])**2+(pts1[i,2]-pts2[ii,2])**2) 
                            #if i != 99:
                            #    d_1dif = math.sqrt((pts1[i+1,0]-pts2[ii,0])**2+(pts1[i+1,1]-pts2[ii,1])**2+(pts1[i+1,2]-pts2[ii,2])**2) 
                            #else:
                            #    d_1dif = math.sqrt((pts1[0,0]-pts2[ii,0])**2+(pts1[0,1]-pts2[ii,1])**2+(pts1[0,2]-pts2[ii,2])**2) 
                            #if ii != 99:
                            #    d_2dif = math.sqrt((pts1[i,0]-pts2[ii+1,0])**2+(pts1[i,1]-pts2[ii+1,1])**2+(pts1[i,2]-pts2[ii+1,2])**2) 
                            #else:
                            #    d_2dif = math.sqrt((pts1[i,0]-pts2[0,0])**2+(pts1[i,1]-pts2[0,1])**2+(pts1[i,2]-pts2[0,2])**2)                                 

                            '''
                            #shift link if applicable
                            if d_main > d_1dif:
                                if i == 99:
                                    i = 0
                                else:
                                    i += 1
                                iii += 1
                            elif d_main > d_2dif:
                                if ii == 99:
                                    ii = 0
                                else:
                                    ii += 1
                                iii += 1
                            '''

                            #create points to add to sp_ref  -- add point cloudes to mat_list -- same order as splines!
                            xdif = -pts1[i,0]+pts2[ii,0]
                            ydif = -pts1[i,1]+pts2[ii,1]
                            zdif = -pts1[i,2]+pts2[ii,2]

                            #create links between each of the 100 points
                            #for efficiency all intermediate splines between 2 specific main splines done here
                            for iv, c in enumerate(cnt):
                                #based on number of plies in this location split these vectors proportionally
                                x_loc = iv*(xdif/len(cnt))+pts1[i,0]
                                y_loc = iv*(ydif/len(cnt))+pts1[i,1]
                                z_loc = iv*(zdif/len(cnt))+pts1[i,2]

                                l_sp[iv] = np.concatenate((l_sp[iv],np.asarray([[x_loc,y_loc,z_loc,0]])),axis = 0)

                            #working with hundred points but possibly with different starting locations
                            if i == no_p-1:
                                i = 0
                            else:
                                i += 1
                            if ii == no_p-1:
                                ii = 0
                            else:
                                ii += 1
                            iii = iii + 1      

                        for iv, c in enumerate(cnt):
                            #delete first line of each matrix  
                            l_sp[iv] = np.delete(l_sp[iv],0,axis=0)
                            #append reference to spls
                            spls.append(c)
                            #append points to mat_list
                            mat_list.append(l_sp[iv])
                            #done.append.. ... the full spline to avoid dupe
                            close_list.append(cls1)
                            done.append(c)

            #only finish layup definition if no errors have been trigered
            if error != True:
                #spline reference list
                sp_ref = str(sp_ref)
                sp_ref = sp_ref.replace(" ","")
                str_def += str(sp_ref) + "\n \n"

                if str_sd != "":
                    str_def += str_sd

                #This requires an option for mixed materials. 
                str_def += "\n[MATERIALS] \n"
                str_def += str(values['klic16'])+"\n"
                str_def += "["+str(values["klic"])+"]\n\n"
                
                str_def += "\n[SPLINES] \n \n"
                
                #points for each spline
                for i, sp in enumerate(spls):
                    str_def += sp +","+str(close_list[i])+"\n"
                    
                    tt = str(mat_list[i])
                    #tt = np.array(map(str, mat_list[i]))
                    #array(['0', '33', '4444522'], dtype='|S7')
                    tt = tt.replace("[["," ")
                    tt = tt.replace("[","")
                    tt = tt.replace("]","")    
                    str_def += str(tt) + "\n\n___{end_spline}___\n\n"
                
                #edge spline
                str_def += "[EDGE SPLINE]"+"\n"
                ep = str(edge_points)
                #ep = np.array(map(str, edge_points))
                tt = ep.replace("[["," ")
                tt = tt.replace("[","")
                tt = tt.replace("]","") 
                str_def += str(tt) + "\n\n___{end_edge_spline}___\n\n"
                #add sharpness of points as 4th dimension? to disconect splines?
                
                txt_file = CADfile.replace(".CatPart","_layup.txt")
                
                #if file exists, check that user is ok with over-write
                if os.path.isfile(txt_file):
                    ch = sg.popup_yes_no("Layup Definition file already exists, continuing will replace the old file.\
                                          Do you want to Continue?",  title="YesNo",keep_on_top=True)
                    if str(ch) == "Yes":
                        with open(txt_file, "w") as text_file:
                            text_file.write(str_def)
                        sg.Popup("Layup file has been created, stored as:"+str(txt_file),keep_on_top=True)

                else:
                    with open(txt_file, "a") as text_file:
                        text_file.write(str_def)
                    sg.Popup("Layup file has been created, stored as:"+str(txt_file),keep_on_top=True)

        #enforce unique spline names
    if event in 'matN':   
           
        #layout for material imports
        seznam3 = ["GFRP","CFRP","other"]

        layout33 = [[sg.Text('Material name:',size=(s1,1)),sg.InputText("", key='mn',size=(s2, 1))],
        [sg.Text('E1:',size=(s1,1)),sg.InputText("", key='E1',size=(s2, 1))],
        [sg.Text('E2:',size=(s1,1)),sg.InputText("", key='E2',size=(s2, 1))],
        [sg.Text('G12:',size=(s1,1)),sg.InputText("", key='G12',size=(s2, 1))],
        [sg.Text('G23:',size=(s1,1)),sg.InputText("", key='G23',size=(s2, 1))],
        [sg.Text('v12:',size=(s1,1)),sg.InputText("", key='v12',size=(s2, 1))],
        [sg.Text('source:',size=(s1,1)),sg.InputText("", key='source',size=(s2, 1))],
        [sg.Text('fibre diameter:',size=(s1,1)),sg.InputText("", key='fd',size=(s2, 1))],
        [sg.Text('density:',size=(s1,1)),sg.InputText("", key='dens',size=(s2, 1))],
        [sg.Text('permeability cf.:',size=(s1,1)),sg.InputText("", key='perm',size=(s2, 1))],
        [sg.Text('type:',size=(s1,1)),sg.Combo(seznam3,size=(s2,1),disabled=False,key='type')],
        [sg.Button('Save material',key='save_mat',size=(15,1))]]

        window33 = sg.Window('Material Definition', layout33, default_element_size=(12,1),size=(400,330),keep_on_top=True)

        while True: 
            #read all potential user inputs
            event33, values33 = window33.read()    
            
            if event33 is None: # way out!    
                break  
            if event33 in 'save_mat':
                rr = True

                with open(lf3, "r") as text_file:
                    maxID = 0
                    for i ,line in enumerate(text_file.readlines()):
                        if line.count(",") > 0 and i != 0:
                            #print("yes")
                            m_r = float(line.split(",")[0])
                            if maxID < m_r:
                                maxID = m_r
                    
                #SQL has been replaced by .txt database
                stre = "\n"+str(int(maxID+1))

                if str(values33['mn']) == "":
                    sg.Popup("Please specify 'Material name'",keep_on_top=True)
                else:
                    stre += ","+ """'"""+str(values33['mn'])+"""'"""

                if str(values33['E1']) == "":
                    sg.Popup("E1 is a compulsory field'",keep_on_top=True)
                    rr = False
                else:
                    try:
                        E1 = float(values33['E1'])
                    except:
                        sg.Popup("E1 must be a number'",keep_on_top=True)
                        rr = False
                    stre += """,'"""+str(E1)+"""'"""

                if str(values33['E2']) == "":
                    sg.Popup("E2 is a compulsory field'",keep_on_top=True)
                    rr = False
                else:
                    try:
                        E2 = float(values33['E2'])
                    except:
                        sg.Popup("E2 must be a number'",keep_on_top=True)
                        rr = False
                    stre += """,'"""+str(E2)+"""'"""

                if str(values33['G12']) == "":
                    sg.Popup("G12 is a compulsory field'",keep_on_top=True)
                    rr = False
                else:
                    try:
                        G12 = float(values33['G12'])
                    except:
                        sg.Popup("G12 must be a number'",keep_on_top=True)
                        rr = False
                    stre += """,'"""+str(G12)+"""'"""

                if str(values33['G23']) == "":
                    sg.Popup("G23 is a compulsory field'",keep_on_top=True)
                    rr = False
                else:
                    try:
                        G23 = float(values33['G23'])
                    except:
                        sg.Popup("G23 must be a number'",keep_on_top=True)
                        rr = False
                    stre += """,'"""+str(G23)+"""'"""
                
                if str(values33['v12']) == "":
                    sg.Popup("v12 is a compulsory field'",keep_on_top=True)
                    rr = False
                else:
                    try:
                        v12 = float(values33['v12'])
                    except:
                        sg.Popup("v12 must be a number'",keep_on_top=True)
                        rr = False
                    stre += """,'"""+str(v12)+"""'"""

                if str(values33['source']) != "":

                    stre += """,'"""+str(values33['source'])+"""'"""

                if str(values33['fd']) == "":
                    sg.Popup("fibre diameter is a compulsory field'",keep_on_top=True)
                    rr = False
                else:
                    try:
                        fd = float(values33['fd'])
                    except:
                        sg.Popup("fibre diameter must be a number'",keep_on_top=True)
                        rr = False

                    stre += """,'"""+str(fd)+"""'"""

                if str(values33['dens']) != "":
                    try:
                        dd = float(values33['dens'])
                    except:
                        sg.Popup("density must be a number'",keep_on_top=True)
                        rr = False

                    stre += """,'"""+str(dd)+"""'"""

                if str(values33['perm']) != "":
                    try:
                        pcf = float(values33['perm'])
                    except:
                        sg.Popup("permeability coefficient must be a number'",keep_on_top=True)
                        rr = False
                    stre += """,'"""+str(pcf)+"""'"""

                if str(values33['type']) != "":

                    stre += """,'"""+str(values33['type'])+"""'"""
               
                lf3 = values['location']+"/"+"LD_layup_database.txt"

                with open(lf3, "a") as text_file:
                    text_file.write(stre)
                    sg.Popup("Material "+str(maxID+1)+" has been stored",keep_on_top=True)
                

#separate script for adding thicknesses 

#yet another script for 2D cross sections 

#the following should be usd to run executable in CATIA

'''
Language="VBSCRIPT"

Sub CATMain()
dim sh,s
Set sh = CreateObject("WScript.Shell")


s ="f:\etc\etc.exe"
sh.Run s, 1, false
End Sub
'''
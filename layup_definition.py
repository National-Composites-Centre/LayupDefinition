
from jsonic import serialize, deserialize
import pprint

import win32com.client.dynamic
import pywintypes
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize) #for troubleshooting only
from vecEX3 import wrmmm
#BEING REPLACED #import PySimpleGUI as sg
import os
from datetime import date
import math
from utilities import sharpness , clean_json , MatSel

#from secondary_UIs import newMat #currently unused cleanup - because of parameter passing issues between UI's in differnt scripts
#from utilities import sharpness

#replacing PySimpleGUI by Kivy
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView

from kivy.uix.popup import Popup

from kivy.lang import Builder
from kivy.properties import StringProperty

#from LD STANDARD file
from CompoST import CompositeStandard as cs


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

def SplinesToClouds(spNames,no_p = 200,CADfile=""):
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
            print("direction reversed") 

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
        part1.Update()

    except:
        content=Button(text="Please make sure geometric set called 'main_shape' exits,"
        +" and contains only main layup surface (tool), called 'MainS'.", size_hint_y=None,height=100,halign='center',valign='middle')
        content.text_size = (400,None)
        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(0.7, 0.3))
        content.bind(on_press=popup.dismiss)
        popup.open()
        return(mat_list,[0,0,0],False,closed_list)

    
    part1.Update()
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



def AddMat(self,obj):
    print("c")

def CLF(self):
        
    no_p = self.no_p #this needs fixing, no idea how to pass variable from ui

    #first check if multi-material, appropriate number of lines
    if self.cb3.active  == True:
        mat_count =  self.layout.children[59].text.count(",") #counts an empty line break hence +1 below 
        ply_count =  self.layout.children[63].text.count(",")+1
        if mat_count != ply_count:
            content=Button(text="Please make sure list of materials is same lenght as list of plies,\nfor multi-material option")
            popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
            content.bind(on_press=popup.dismiss)
            popup.open()
            #should prevent rest of layup generation
            return()


    #Upon running the layup generation
    i = 1
    #spline list
    spls = []
    while i < 13:
        if self.layout.children[43-i*3].text != "":
            spls.append(self.layout.children[43-i*3].text)
        i = i + 1

    #TODO:
        #IF second spline is to be used,the order of stored splines has to be considred not to interfere with the others
    #
    #i = 1
    #while i < 13:
    #    if self.layout.children[43-i*3].text != "":
    #        spls.append(self.layout.children[43-i*3].text)
    #    i = i + 1

    #check if folder select includes part
    if "." in self.layout.children[69].text:
        #assume no other . in name, otherwise ... TODO
        if (self.layout.children[69].text.split(".")[1]).lower() == "catpart":
            if (self.layout.children[72].text).lower() in (self.layout.children[69].text.split(".")[0]).lower():
                CADfile = self.layout.children[69].text.split(".")[0]
            else:
                content=Button(text="""Selected part is not loaded in CATIA. \n Specify correct part, or specify folder and part separately \n; not using SelectFile button""")
                popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                content.bind(on_press=popup.dismiss)
                popup.open()
                #should prevent rest of layup generation
                return()
        else:
            content=Button(text="The selected file has to be CATIA part file (for now..)")
            popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
            content.bind(on_press=popup.dismiss)
            popup.open()
            #should prevent rest of layup generation
            return()
        
    else:
        #seems like part was specified manually
        CADfile = self.layout.children[69].text+"\\"+self.layout.children[72].text
    print(CADfile)
    

    #Option for basic tool (not circular)

    if self.layout.children[53].active == True:
        #create points delimiting layers
        mat_list, edge_points,rrun,close_list = SplinesToClouds(spls,CADfile=CADfile)

        if rrun == True:

            #add column defining spline interuptions (i.e. corners)
            i = 0
            while i < len(mat_list):
                #for all defined splines
                mat_list[i], breaks = sharpness(mat_list[i])
                i = i + 1

            #for edge points - corners
            edge_points, breaks = sharpness(edge_points)
            
            FL = cs.CompositeDB()
            FL.allComposite = []

            #load material database to select materials from
            matDatabase = MatSel(CADfile)

            #start constructing the layup .txt file
            FL.fileMetadata.layupDefinitionVersion = self.layout.children[71].text
            #At initial creation of JSON file last modification and author are the same
            FL.fileMetadata.lastModifiedBy = str(os.getlogin())
            FL.fileMetadata.author = str(os.getlogin())

            #basic info / header
            today = date.today()
            d1 = today.strftime("%d/%m/%Y")
            FL.fileMetadata.lastModified = str(d1)
            
            #cad reference file"
            FL.fileMetadata.cadFile = self.layout.children[72].text
            FL.fileMetadata.cadFilePath = self.layout.children[69].text

            #check and initiate geometry
            if FL.allGeometry == None:
                FL.allGeometry = []

            noG = len(FL.allGeometry)

            sp_temp_points = []
            
            #delimiting spline ref
            for ii, pt in enumerate(edge_points[:,0]):
                    sp_temp_points.append(cs.Point(x=edge_points[ii,0],y=edge_points[ii,1],z=edge_points[ii,2]))
            FL.allGeometry.append(cs.Spline(points=sp_temp_points, memberName = "edge",ID = (FL.fileMetadata.maxID+1)))
            FL.fileMetadata.maxID += 1
            
            spline_refs = []
            noG = noG + 1

            #print("spls",spls)
            #Save reference splines
            for i,spl in enumerate(spls):
                #turn points into point classes
                sp_temp_points = []
                #pickr corresponding point matrix
                mx = mat_list[i]
                for ii, pt in enumerate(mx[:,0]):
                    sp_temp_points.append(cs.Point(x=mx[ii,0],y=mx[ii,1],z=mx[ii,2]))

                FL.allGeometry.append(cs.Spline(points=sp_temp_points, memberName = spl,ID = (FL.fileMetadata.maxID+1),breaks=breaks))
                FL.fileMetadata.maxID += 1
                spline_refs.append(spl)

                noG = noG + 1

            #the layup itself
            seq = str(self.layout.children[63].text)
            seq = seq.split("[")[1]
            seq = seq.split("]")[0]

            FL.allComposite.append(cs.Sequence(ID = (FL.fileMetadata.maxID+1)))
            FL.fileMetadata.maxID += 1
            #initiate material database 
            if FL.allMaterials == None:
                FL.allMaterials = []
            gc = len(FL.allComposite)

            refG = FL.allComposite[gc-1]
            refG.subComponents = []
            #loop throug plies

            #list of stored materials
            stored_mat = []
            for i, s in enumerate(seq.split(",")[:]):
                if self.layout.children[60].active == True:
                    mat = self.layout.children[59].text
                elif self.layout.children[57].active == True :
                    mat = self.layout.children[59].text.split(",")[i]

                #find if dropped off
                dropped = False
                cc = 38
                drop = self.layout.children[cc].text
                d_ref = "edge"
                while drop != "":
                    for dr in drop.split(",")[:]:
                        if dr == str(i+1):
                            if dropped == True:
                                content=Button(text="At least one layer is dropped-off twice. Please fix to proceed.")
                                popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                                content.bind(on_press=popup.dismiss)
                                popup.open()
                                return()
                            else:
                                dropped == True
                                #find which spline corresponds to drop-off
                                d_ref = self.layout.children[cc+2].text
                    cc = cc - 3
                    drop = self.layout.children[cc].text

                #To turn name refs into number refs
                for spline in FL.allGeometry:
                    if type(spline) == type(cs.Spline()):
                        if spline.memberName == d_ref:
                            ID_ref = spline.ID


                pic = cs.Piece(splineRelimitationRef = ID_ref,ID = (FL.fileMetadata.maxID+1))
                FL.fileMetadata.maxID += 1

                #create piece delimited by correct spline 
                #CORE adjusted
                if mat not in stored_mat:
                    mat_found = False
                    for m in matDatabase:
                        #print(m.memberName,mat)
                        if mat == m.memberName:
                            #Add ID as material is being used
                            m.ID = FL.fileMetadata.maxID+1
                            FL.allMaterials.append(m)
                            FL.fileMetadata.maxID += 1
                            
                            mat_found = True
                            break

                    if mat_found ==False:
                        content=Button(text="One of the materials specified is not available in database ("+mat+").\nPlease change the material or add to database.")
                        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                        content.bind(on_press=popup.dismiss)
                        popup.open()
                        return()

                    #preventing re-storing of material
                    stored_mat.append(mat)

                else:
                    #make sure correct material is stored in m, if it has already been discovered and save
                    for anyM in FL.allMaterials:
                        if anyM.memberName ==mat:
                            m = anyM

                refG.subComponents.append(cs.Ply(orientation=s,material=m,cutPieces=[pic],ID = (FL.fileMetadata.maxID+1),splineRelimitationRef = ID_ref))
                FL.fileMetadata.maxID += 1

            

            #txt_file = CADfile.replace(".CatPart","_layup.json")
            #txt_file = txt_file.replace(".txt","_layup.json")
            txt_file = CADfile+"_layup.json"
            
            #if file exists, check that user is ok with over-write
            if os.path.isfile(txt_file):
                
                #Kivy is horrible with pop-ups, so dedicated Tkinter question
                import tkinter as tk
                
                root = tk.Tk()
                frame = tk.Frame()
                frame.pack(fill=tk.BOTH, expand=True)

                result = "no"
                
                def clickButton1():
                    json_str = serialize(FL, string_output = True)
                    json_str = clean_json(json_str)

                    #save as file
                    with open(txt_file, 'w') as out_file:
                        out_file.write(json_str)

                    content=Button(text="Layup file has been created, stored as: \n"+str(txt_file)+"\n [Click to close pop-up]")
                    popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                    content.bind(on_press=popup.dismiss)
                    popup.open()
                    root.destroy()
                
                def clickButton2():
                    root.destroy()

                
                label = tk.Label(frame, text = "Corresponding file already exists, do you want it replaced?")
                button1 = tk.Button(frame, text="Yes", command=clickButton1)
                button2 = tk.Button(frame, text="No", command=clickButton2)
                label.pack()
                button1.pack()
                button2.pack()
                root.mainloop()       

            else:
                json_str = serialize(FL, string_output = True)
                #json_str = pprint.pformat(json_str,indent=2).replace("'",'"')
                json_str = clean_json(json_str)

                #save as file
                with open(txt_file, 'w') as out_file:
                    out_file.write(json_str)

                content=Button(text="Layup file has been created, stored as: \n"+str(txt_file)+"\n [Click to close pop-up]")
                popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                content.bind(on_press=popup.dismiss)
                popup.open()

    elif self.layout.children[55].active == True:
        #TODO this was created as copy of default tool with drop-offs, this is currently very basic mandrel implementation
        #and it does not account for any drop-offs


        
        FL = cs.CompositeDB()
        FL.allComposite = []

        #load material database to select materials from
        matDatabase = MatSel(CADfile)

        #start constructing the layup .txt file
        FL.fileMetadata.layupDefinitionVersion = self.layout.children[71].text
        #At initial creation of JSON file last modification and author are the same
        FL.fileMetadata.lastModifiedBy = str(os.getlogin())
        FL.fileMetadata.author = str(os.getlogin())

        #basic info / header
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        FL.fileMetadata.lastModified = str(d1)
        
        #cad reference file"
        FL.fileMetadata.cadFile = self.layout.children[72].text
        FL.fileMetadata.cadFilePath = self.layout.children[69].text

        #check and initiate geometry
        if FL.allGeometry == None:
            FL.allGeometry = []

        noG = len(FL.allGeometry)

        #the layup itself
        seq = str(self.layout.children[63].text)
        seq = seq.split("[")[1]
        seq = seq.split("]")[0]

        FL.allComposite.append(cs.Sequence(ID = (FL.fileMetadata.maxID+1)))
        FL.fileMetadata.maxID += 1
        #initiate material database 
        if FL.allMaterials == None:
            FL.allMaterials = []
        gc = len(FL.allComposite)

        refG = FL.allComposite[gc-1]
        refG.subComponents = []
        #loop throug plies

        #list of stored materials
        stored_mat = []
        for i, s in enumerate(seq.split(",")[:]):
            if self.layout.children[60].active == True:
                mat = self.layout.children[59].text
            elif self.layout.children[57].active == True :
                mat = self.layout.children[59].text.split(",")[i]

            #find if dropped off (currently cannot)
            dropped = False


            if mat not in stored_mat:
                mat_found = False
                for m in matDatabase:
                    #print(m.memberName,mat)
                    if mat == m.memberName:
                        #Add ID as material is being used
                        m.ID = FL.fileMetadata.maxID+1
                        FL.allMaterials.append(m)
                        FL.fileMetadata.maxID += 1
                        
                        mat_found = True
                        break

                if mat_found ==False:
                    content=Button(text="One of the materials specified is not available in database ("+mat+").\nPlease change the material or add to database.")
                    popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                    content.bind(on_press=popup.dismiss)
                    popup.open()
                    return()

                #preventing re-storing of material
                stored_mat.append(mat)

            else:
                #make sure correct material is stored in m, if it has already been discovered and save
                for anyM in FL.allMaterials:
                    if anyM.memberName ==mat:
                        m = anyM

            refG.subComponents.append(cs.Ply(orientation=s,material=m,ID = (FL.fileMetadata.maxID+1)))
            FL.fileMetadata.maxID += 1

        

        #txt_file = CADfile.replace(".CatPart","_layup.json")
        #txt_file = txt_file.replace(".txt","_layup.json")
        txt_file = CADfile+"_layup.json"
        
        #if file exists, check that user is ok with over-write
        if os.path.isfile(txt_file):
            
            #Kivy is horrible with pop-ups, so dedicated Tkinter question
            import tkinter as tk
            
            root = tk.Tk()
            frame = tk.Frame()
            frame.pack(fill=tk.BOTH, expand=True)

            result = "no"
            
            def clickButton1():
                json_str = serialize(FL, string_output = True)
                json_str = clean_json(json_str)

                #save as file
                with open(txt_file, 'w') as out_file:
                    out_file.write(json_str)

                content=Button(text="Layup file has been created, stored as: \n"+str(txt_file)+"\n [Click to close pop-up]")
                popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                content.bind(on_press=popup.dismiss)
                popup.open()
                root.destroy()
            
            def clickButton2():
                root.destroy()

            
            label = tk.Label(frame, text = "Corresponding file already exists, do you want it replaced?")
            button1 = tk.Button(frame, text="Yes", command=clickButton1)
            button2 = tk.Button(frame, text="No", command=clickButton2)
            label.pack()
            button1.pack()
            button2.pack()
            root.mainloop()       

        else:
            json_str = serialize(FL, string_output = True)
            #json_str = pprint.pformat(json_str,indent=2).replace("'",'"')
            json_str = clean_json(json_str)

            #save as file
            with open(txt_file, 'w') as out_file:
                out_file.write(json_str)

            content=Button(text="Layup file has been created, stored as: \n"+str(txt_file)+"\n [Click to close pop-up]")
            popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
            content.bind(on_press=popup.dismiss)
            popup.open()

    #enforce unique spline names
def sp1(self):
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
        i = 0
        while i < 13:
            #Dont ask me why 40-i*3.... just Kivy things
            if self.layout.children[40-i*3].text =="":
                self.layout.children[40-i*3].text = sel_obj
                break
            i = i + 1
            if i == 13:
                print("currently only 12 splines are supported")
    except:
        content=Button(text='please select an object first')
        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
        content.bind(on_press=popup.dismiss)
        popup.open()
        


def sp2(self,obj):
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
        i = 0
        while i < 13:
            #Dont ask me why 39-i*3.... just Kivy things
            if self.layout.children[39-i*3].text =="":
                self.layout.children[39-i*3].text = sel_obj
                break
            i = i + 1
            if i == 13:
                print("currently only 12 splines are supported")
    except:
        content=Button(text='please select an object first')
        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
        content.bind(on_press=popup.dismiss)
        popup.open()


#def select1(self,obj):
#    print("no")





    

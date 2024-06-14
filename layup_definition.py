# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:34:14 2022

@author: jakub.kucera
"""

'''
import kivy

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty

def yesno():
    Builder.load_string('''
#    <ConfirmPopup>:
#        cols:1
#        Label:
#            text: root.text
#        GridLayout:
#            cols: 2
#            size_hint_y: None
#            height: '44sp'
#            Button:
#                text: 'Yes'
#                on_release: root.dispatch('on_answer','yes')
#            Button:
#                text: 'No'
#                on_release: root.dispatch('on_answer', 'no')
''')

    class ConfirmPopup(GridLayout):

        text = StringProperty()
        
        def __init__(self,**kwargs):
            self.register_event_type('on_answer')
            super(ConfirmPopup,self).__init__(**kwargs)
            
        def on_answer(self, *args):
            pass	

    class ConfirmSave(App):
        def build(self):
            content = ConfirmPopup(text="Layup Definition file already exists, continuing will replace the old file.Do you want to Continue?")
            content.bind(on_answer=self._on_answer)
            self.popup = Popup(title="Answer Question",
                                content=content,
                                size_hint=(None, None),
                                size=(650,150),
                                auto_dismiss= False)
            self.popup.open()
            
        def _on_answer(self, instance, answer):
            print("USER ANSWER: " , repr(answer))
            self.popup.dismiss()
		
    if __name__ == '__main__':
	    ConfirmPopup().run()

'''

import win32com.client.dynamic
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize) #for troubleshooting only
from vecEX3 import wrmmm
#BEING REPLACED #import PySimpleGUI as sg
import os
from datetime import date
import math
from utilities import sharpness

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

#from LD import Popup


version = "3.1"

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
        content=Button(text="Please make sure geometric set called 'main_shape' exits,"
                 +" and contains only main layup surface (tool), called 'MainS'")
        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(0.5, 0.3))
        content.bind(on_press=popup.dismiss)
        popup.open()

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



def AddMat(self,obj):
    print("c")

def CLF(self):
        
    no_p = self.no_p #this needs fixing, no idea how to pass variable from ui

    #Upon running the layup generation
    i = 1
    #spline list
    spls = []
    while i < 13:
        if self.layout.children[40-i*3].text != "":
            spls.append(self.layout.children[40-i*3].text)
        i = i + 1

    i = 1
    while i < 13:
        if self.layout.children[39-i*3].text != "":
            spls.append(self.layout.children[39-i*3].text)
        i = i + 1

    #might have a nicer way to reference than integer... 
    CADfile = self.layout.children[66].text+"\\"+self.layout.children[69].text+".txt"
    print(CADfile)
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
        str_def += str(self.layout.children[60].text)+"\n"
        
        #preparing to loop through layers, to define drop-offs
        lam = self.layout.children[60].text
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
        while i < 13:
            #38 onwards are the drop-off indicating integers 
            if self.layout.children[38-i*3].text != "":
                tv = self.layout.children[38-i*3].text
                ii = 0
                cnt = tv.count(",")
                while ii < cnt+1:
                    tvx = int(tv.split(",")[ii])
                    
                    loc_sp = self.layout.children[40-i*3].text
                    #checking the layer number fits within the total layup listed
                    if tvx > cnt_l:
                        content=Button(text="layer "+str(tvx)+" is not listed above. Please adjust your definition.")
                        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                        content.bind(on_press=popup.dismiss)
                        popup.open()
                        error = True
                    else:
                        #check that no layer is dropped-off twice
                        if tvx in assigned:
                            content=Button(text="layer "+str(tvx)+" is assigned to multiple limits. Please adjust your definition.")
                            popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                            content.bind(on_press=popup.dismiss)
                            popup.open()
                            error = True
                        else:
                            if self.layout.children[39-i*3].text == "":
                                sp_ref[tvx-1] = loc_sp
                                assigned.append(tvx)
                            else:
                                #this else exists for the purposes of 2-spline delimitation

                                #the below replaces spline by composite spline name
                                #this name will required additional spline creation based on this 
                                sp_ref[tvx-1] = loc_sp+"+++"+self.layout.children[39-i*3].text+"+++"+str(tvx)
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
                        content=Button(text="To splines specified for delimitation, but one is closed and one open spline.")
                        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                        content.bind(on_press=popup.dismiss)
                        popup.open()
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

            if self.str_sd != "":
                str_def += self.str_sd

            #This requires an option for mixed materials. 
            str_def += "\n[MATERIALS] \n"
            if self.layout.children[57].active == True:
                str_def += "Uniform material\n"
            if self.layout.children[54].active == True:
                str_def += "Variable material"

            str_def += "["+self.layout.children[56].text+"]\n\n"
            
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
                ch = "Yes" #yesno()
                print("ch",ch)

                if str(ch) == "Yes":
                    with open(txt_file, "w") as text_file:
                        text_file.write(str_def)

                    content=Button(text="Layup file has been created, stored as: \n"+str(txt_file)+"\n [Click to close pop-up]")
                    popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
                    content.bind(on_press=popup.dismiss)
                    popup.open()

            else:
                print(txt_file)
                with open(txt_file, "a") as text_file:
                    text_file.write(str_def)

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
        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(0.5, 0.2))
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
        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(0.5, 0.2))
        content.bind(on_press=popup.dismiss)
        popup.open()


def select1(self,obj):
    print("no")

def MatSel(location):
            
        
    lf3 = "LD_layup_database.txt"
    try:

        with open(location+"\\"+lf3, "r") as text_file:

            seznam = []
            for i ,line in enumerate(text_file.readlines()):
                if line.count(",") > 0 and i != 0:
                    #print("yes")
                    m_ref = line.split(",")[1]
                    seznam.append(m_ref)
    except:

        content=Button(text="Material database file was not found in the location specified.\n"
                    +"Therefore an empty materil file has been created, but needs to be populated.")
        popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(0.5, 0.2))
        content.bind(on_press=popup.dismiss)
        popup.open()
        with open(location+"\\"+lf3, 'w') as f:
            f.write("id,Material_name,	E1,	E2,	G12, G23,	v12,"
                    +"	Info_source,	layer_thickness,	density,	perme_coeff, type")
        seznam = ["no material available"]

    return(seznam)


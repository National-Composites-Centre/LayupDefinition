import numpy as np
from numpy.linalg import norm
import math

import win32com.client.dynamic
import numpy as np
import sys

#replacing PySimpleGUI by Kivy
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout

from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView

from kivy.uix.popup import Popup

from kivy.lang import Builder
from kivy.properties import StringProperty

from kivy.uix.dropdown import DropDown
from kivy.base import runTouchApp

from kivy.uix.checkbox import CheckBox

from CompoST import CompositeStandard

def sharpness(mat_list):
    
    w = np.size(mat_list,1)
    l = np.size(mat_list,0)
    breaks = []

    i = 0
    add = np.zeros((l,1))
    mat_list_p = np.append(mat_list, add, axis=1)

    while i < l:
        if i == l-1:
            next_ = mat_list[0,:]
        else:
            next_ = mat_list[i+1,:]

        if i == 0:
            prev = mat_list[l-1,:]
        else:
            prev = mat_list[i-1,:]
        
        this = mat_list[i,:]

        u = next_ - this
        v = prev - this
        c = np.dot(u,v)/norm(u)/norm(v) # -> cosine of the angle
        angle = np.arccos(np.clip(c, -1, 1)) # if you really want the angle
        angle = angle*180/math.pi

        #Thresholds for corners
        #Consider medium threshold where sharp_bn = 1 but previous one is turned 0 to prevent TODO
        #multiple corner points in one corner.

        if angle < 90:
            sharp_bn = 1
            breaks.append(i)
        else:
            sharp_bn = 0
            

        mat_list_p[i,3] = sharp_bn

        i += 1

    return(mat_list_p,breaks)

def clean_json(strin):
    #strin = input json string to clean
    s = strin.replace("{","\n{\n")
    s = s.replace("}","\n}\n")

    tabs = 0
    new_str = ""
    for line in s.split("\n")[:]:
        
        if "}" in line:
            tabs = tabs - 1

        for ii in range(0,tabs):
            new_str += "   "
        new_str += line+"\n"

        if "{" in line:
            tabs = tabs + 1

    return(new_str)

def TK_FS(self):
    #the random argument is just because kivy passes random stuff during on_press... so...

    #TK file selector
    import tkinter as tk
    from tkinter import filedialog

    filetypes = (
        ('catiaFiles','*.CATPart'),
        ('All files', '*.*'),
    )

    # open-file dialog
    root = tk.Tk()
    filename = tk.filedialog.askopenfilename(
        title='Select a file...',
        filetypes=filetypes,
    )
    self.layout.children[66].text = filename


    mat_list = MatSel(self.location.text)

    #generates list of drop-down options if material database JSON is available in selected directory
    if mat_list != ["no material available"]:
        for mt in mat_list: #CHANGE THIS FOR INPUT
            btn = Button(text=mt.memberName, size_hint_y=None, height=22)
            # for each button, LINK TEXT
            btn.bind(on_release=lambda btn: self.dd1.select(btn.text))
            # then add the button inside the dropdown
            self.dd1.add_widget(btn)
    else:
        #included so that applicaiton does not immediately crash if no database
        btn = Button(text="no material available",size_hint_y=None,height=22)
        btn.bind(on_release=lambda btn: self.dd1.select(btn.text))
        # then add the button inside the dropdown
        self.dd1.add_widget(btn)

    root.destroy()
    return(self)


# filename == 'path/to/myfilename.txt' if you type 'myfilename'
# filename == 'path/to/myfilename.abc' if you type 'myfilename.abc'
#test

#mat_list = np.asarray([[1,2,3],[1,3,3],[1,4,3],[1,5,3],[3,5,3]])
#test = sharpness(mat_list)
#print(test)

#test clean_json


'''
with open("D:\\CAD_library_sampling\\TestCad_SmartDFM\\X\\x_test_128.txt","r") as X:
    jstr = str(X.read())
    #print(jstr)
    clean_json(jstr)

'''
from jsonic import serialize, deserialize

def MatSel(location):
    #retreive the names of available materials 
    
    #Currently only works with JSON database
    lf3 = "LD_layup_database"
    seznam = []
    
    
    #remove the file out of file-path
    loc = ""
    for sec in location.split("/")[0:(location.count("/"))]:
        loc += sec+"/"
        #print(loc)
    location = loc

    if location == "":
        seznam = ["no material available"]
    else:
        #allow for database not being immediately available
        #print(location+lf3+".json")
        #try:
            #collects all materials available
        with open(location+lf3+".json", "r") as in_file:
            json_str= in_file.read()
            
            D = deserialize(json_str,string_input=True)
            
            for i ,material in enumerate(D.allMaterials):
                seznam.append(material)
        # except:
        
        #     #TODO consider this to be pop-up
        
        #     print("no JSON material database")
        #     seznam = ["no material available"]
        #     pass

    return(seznam)



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



def sharpness(mat_list):
    
    w = np.size(mat_list,1)
    l = np.size(mat_list,0)

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
        #Consider medium threshold where sharp_bn = 1 but previous one is turned 0 to prevent
        #multiple corner points in one corner.

        if angle < 130:
            sharp_bn = 1
        else:
            sharp_bn = 0

        mat_list_p[i,3] = sharp_bn



        i += 1

    return(mat_list_p)

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


    #print(new_str)

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
    
    for mt in mat_list: #CHANGE THIS FOR INPUT
        btn = Button(text=mt, size_hint_y=None, height=22)
        # for each button, LINK TEXT
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

#TODO THIS is duplicated in Layup definition --- probably better if it lives here and is imported to there!
def MatSel(location):
    #retreive the names of available materials 
    
    #first check JSON database available
            
    #if JSON not available, check for .txt database available
    lf3 = "LD_layup_database"
    seznam = []

    if "." in location:
        location = location.replace(location.split("/")[location.count("/")],"")
        #print("loc fixed",location)

    try:
        with open(location+"\\"+lf3+".json", "r") as in_file:
            json_str= in_file.read()

            D = deserialize(json_str,string_input=True)
            
            for i ,material in enumerate(D.allMaterials):
                seznam.append(material.materialName)
    except:
        print("no JSON material database")
        pass
    
    if seznam == []:
        try:

            with open(location+"\\"+lf3+".txt", "r") as text_file:

                seznam = []
                for i ,line in enumerate(text_file.readlines()):
                    if line.count(",") > 0 and i != 0:
                        #print("yes")
                        m_ref = line.split(",")[1]
                        seznam.append(m_ref)
        except:
            #if neither database is available, create a .txt one empty
            content=Button(text="Material database file was not found in the location specified.\n"
                        +"Therefore an empty materil file has been created, but needs to be populated.")
            popup = Popup(title='User info', content=content,auto_dismiss=False,size_hint=(1.5, 0.15))
            content.bind(on_press=popup.dismiss)
            popup.open()

            seznam = ["no material available"]

    return(seznam)


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

from layup_definition import AddMat, sp1, sp2, CLF, MatSel

import os

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

#tkinter used for pop-ups rn, as kivy is not good with those
import tkinter.messagebox



def on_checkbox_active(checkbox, value):
    print(checkbox)
    if value:
        print('The checkbox', checkbox, 'is active')

    else:
        print('The checkbox', checkbox, 'is inactive')

'''
class MultiMaterial(App):


    Window.size = (200,700)
    def build(self):
        self.noLayers = 0
        self.layout = GridLayout(cols=2,row_force_default=True,row_default_height=32)

        i = 0
        while i < self.noLayers:
            #row1
            self.layout.add_widget(Label(text=str(i)))
            dd1 = DropDown()
            mat_list = MatSel(self.location.text)
            for mt in mat_list: #CHANGE THIS FOR INPUT
                btn = Button(text=mt, size_hint_y=None, height=22)
                # for each button, LINK TEXT
                btn.bind(on_release=lambda btn: dd1.select(btn.text))
                # then add the button inside the dropdown
                dd1.add_widget(btn)
            # create a big main button

            mb1 = Button(text=mat_list[0])
            mb1.bind(on_release=dd1.open)
            # assign the data to the button text.
            dd1.bind(on_select=lambda instance, x: setattr(mb1, 'text', x))
            self.layout.add_widget(mb1)
            i = i + 1
'''
#
'''
#define screens
class MainWindow(Screen):
    pass

class MatWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file('new_window.kv')
'''

class LayupDefinitionApp(App):


    Window.size = (500, 800)
    def build(self):

        seznam2 = ["","uniform","variable"]
        #GUI definition 
        #repeated size of UI - for easer adjusting 
        #sX = [35,25,15,10,20]
        self.no_p = 100 # needs to be edited in Layup_definition (CLF) also...

        #original reference for stacking direction
        x_ref = ""
        y_ref = ""
        z_ref = ""
        x_dir = ""
        y_dir = ""
        z_dir = ""
        self.str_sd = ""

        try: 
            CATIA = win32com.client.Dispatch("CATIA.Application")
            partDocument2 = CATIA.ActiveDocument
            cat_name = CATIA.ActiveDocument.Name
            cat_name = cat_name.split(".CATPart")[0]

        except:

            tkinter.messagebox.showwarning(title="error",message="Please open CATIA and appropriate file first."\
                                +" Make sure all other instances of CATIA are now closed"\
                                     +" (One was likely opened in background right now).")
            sys.exit()

            
        version = "3.2" #3+ is after Kivy transition

        #def_folder = 'C:\\'

        self.layout = GridLayout(cols=3,row_force_default=True,row_default_height=32)
        
        #row1
        self.layout.add_widget(Label(text='Layup file name:'))
        self.layout.add_widget(TextInput(text=cat_name))
        self.layout.add_widget(Label(text='[version='+version+']'))

        #row2
        self.layout.add_widget(Label(text='Location:'))
        self.location = TextInput(text=os.getcwd())  
        self.layout.add_widget(self.location)
        #self.layout.add_widget(Button(text='Select', on_press=self.select1))
        self.layout.add_widget(Label(text=''))

        #row3
        self.layout.add_widget(Label(text='Layup example format:'))
        self.layout.add_widget(Label(text='[0,90,-45,45]'))
        self.layout.add_widget(Label(text=''))

        #row3 and a half ...
        self.layout.add_widget(Label(text='Overall layup:'))
        self.layout.add_widget(TextInput(text='[]'))
        self.layout.add_widget(Label(text=''))
        
        #row4
        self.layout.add_widget(Label(text='Uniform material:'))
        self.cb2 = CheckBox(active = True,on_press=self.cb_sync_1)   
        self.layout.add_widget(self.cb2)
        dd1 = DropDown()
        mat_list = MatSel(self.location.text)
        for mt in mat_list: #CHANGE THIS FOR INPUT
            btn = Button(text=mt, size_hint_y=None, height=22)
            # for each button, LINK TEXT
            btn.bind(on_release=lambda btn: dd1.select(btn.text))
            # then add the button inside the dropdown
            dd1.add_widget(btn)
        # create a big main button

        mb1 = Button(text=mat_list[0])
        mb1.bind(on_release=dd1.open)
        # assign the data to the button text.
        dd1.bind(on_select=lambda instance, x: setattr(mb1, 'text', x))
        self.layout.add_widget(mb1)

        #row4.5
        self.layout.add_widget(Label(text='Variable material:'))
        self.cb3 = CheckBox(active = False,on_press=self.cb_sync_2)  
        self.layout.add_widget(self.cb3)
        self.layout.add_widget(Button(text='select materials', on_press=self.mm))  #adjust button functionality

        self.cb2.bind(active= on_checkbox_active) #link these two ... no working...
        self.cb3.bind(active= on_checkbox_active)  

        #row5
        self.layout.add_widget(Button(text='Stacking direction', on_press=AddMat)) #CHANGE FUNCTION
        #add checkbox later....
        cb1 = CheckBox(active = False)
        cb1.bind(active= on_checkbox_active)    
        self.layout.add_widget(cb1)
        self.layout.add_widget(Label(text=' <== Optional'))

        #row6
        self.layout.add_widget(Button(text='Spline 1 - interactive', on_press=self.sp1_1))
        self.layout.add_widget(Button(text='Spline 2 - interactive', on_press=self.sp2_2))
        self.layout.add_widget(Button(text='Add new material', on_press=AddMat))

        #row7
        self.layout.add_widget(Label(text=''))
        self.layout.add_widget(Label(text=''))
        self.layout.add_widget(Label(text=''))

        #row8
        self.layout.add_widget(Label(text='Spline 1'))
        self.layout.add_widget(Label(text='Spline 2 (optional)'))
        self.layout.add_widget(Label(text='e.g. "1,4"'))

        nr = 12 # number of spline rows
        for I in range(0,nr):

            self.layout.add_widget(TextInput(text=''))
            self.layout.add_widget(TextInput(text=''))
            self.layout.add_widget(TextInput(text=''))

        #rowX-1
        self.layout.add_widget(Label(text=''))
        self.layout.add_widget(Label(text=''))
        self.layout.add_widget(Label(text=''))

        #rowX
        self.layout.add_widget(Label(text=''))
        self.layout.add_widget(Button(text='Create layup file', on_press=self.CLFr))

        return(self.layout)
        #return(kv)
    
    #The below passing as to happen because within button one cannot (for some reasons) specify variables going into function

    def cb_sync_1(self,obj):
        if self.cb3.active == True:
            self.cb3.active = False
        else:
            self.cb3.active = True
        return(self)

    def cb_sync_2(self,obj):
        if self.cb2.active == True:
            self.cb2.active = False
        else:
            self.cb2.active = False
        return(self) 


    def sp1_1(self,obj):
        self = sp1(self)
        return(self)

    def sp2_2(self,obj):
        self = sp2(self)
        return(self)

    def CLFr(self,obj):
        self = CLF(self)
        return(self)
    
    def mm(self,obj):
        if self.cb3.active == True:
            print("multi-material currently not available")
            #MultiMaterial().run()
        else:
            #turn print into pop-up!
            print("multi-material must be selected")
        return(self)
    

    
    
LayupDefinitionApp().run()

#eventually implement tooltips: 

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
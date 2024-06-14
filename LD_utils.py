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

def getPart():
    #try: 
    CATIA = win32com.client.Dispatch("CATIA.Application")
    partDocument2 = CATIA.ActiveDocument
    cat_name = CATIA.ActiveDocument.Name
    cat_name = cat_name.split(".CATPart")[0]

    #except:
    #    cat_name = ""
    return(cat_name)

class MainWindow(Screen):
    pass


class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


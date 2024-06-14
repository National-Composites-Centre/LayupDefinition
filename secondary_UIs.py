import win32com.client.dynamic
import numpy as np
import sys
#np.set_printoptions(threshold=sys.maxsize) #for troubleshooting only
from vecEX3 import wrmmm
import PySimpleGUI as sg
import os
from datetime import date
import math

def newMat(sX,values):
    #layout for material imports
    seznam3 = ["GFRP","CFRP","other"]

    

    layout33 = [[sg.Text('Material name:',size=(sX[1],1)),sg.InputText("", key='mn',size=(sX[0], 1))],
    [sg.Text('E1:',size=(sX[1],1)),sg.InputText("", key='E1',size=(sX[0], 1))],
    [sg.Text('E2:',size=(sX[1],1)),sg.InputText("", key='E2',size=(sX[0], 1))],
    [sg.Text('G12:',size=(sX[1],1)),sg.InputText("", key='G12',size=(sX[0], 1))],
    [sg.Text('G23:',size=(sX[1],1)),sg.InputText("", key='G23',size=(sX[0], 1))],
    [sg.Text('v12:',size=(sX[1],1)),sg.InputText("", key='v12',size=(sX[0], 1))],
    [sg.Text('source:',size=(sX[1],1)),sg.InputText("", key='source',size=(sX[0], 1))],
    [sg.Text('fibre diameter:',size=(sX[1],1)),sg.InputText("", key='fd',size=(sX[0], 1))],
    [sg.Text('density:',size=(sX[1],1)),sg.InputText("", key='dens',size=(sX[0], 1))],
    [sg.Text('permeability cf.:',size=(sX[1],1)),sg.InputText("", key='perm',size=(sX[0], 1))],
    [sg.Text('type:',size=(sX[1],1)),sg.Combo(seznam3,size=(sX[0],1),disabled=False,key='type')],
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
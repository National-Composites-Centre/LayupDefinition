

#replacing PySimpleGUI by Kivy
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout

from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown

import subprocess
import os

from layup_definition import MatSel

def MM(location,plies):
    class MixedMat(App):


        def build(self):
            self.h = 130
            self.plies = plies
            self.layers = 0
            Window.size = (300, self.h)

            self.layout = GridLayout(cols=2,row_force_default=True,row_default_height=23)
            self.location = location
            
            #row0
            self.layout.add_widget(Button(text='Finished!', on_press=self.Finish))
            self.layout.add_widget(Label(text=''))

            #row0
            self.layout.add_widget(Label(text=''))
            self.layout.add_widget(Label(text=''))

            #row0
            #self.layout.add_widget(Button(text='Add Ply', on_press=self.ADDP))
            #self.layout.add_widget(Label(text=''))

            #row1
            self.layout.add_widget(Label(text='Ply no.'))
            self.layout.add_widget(Label(text='Material'))

            for ii in range(0,self.plies):
                self.ADDP(self)
            


            return(self.layout)
        

        def ADDP(self):
            self.layers = self.layers + 1
            self.layout.add_widget(Label(text='Ply '+str(self.layers)))
            dd1 = DropDown()
            mat_list = MatSel(self.location)
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
            self.h = self.h + 23
            
            Window.size = (300, self.h)

            return(self)   
        def Finish(self,obj):

            ply_mats = []
            for i in range(0,self.layers):
                ply_mats = [self.layout.children[0+i*2].text]+ply_mats

            print(ply_mats)



            return(self)

    MixedMat().run()

MM('C:\\code\\fls',3)






'''

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
'''
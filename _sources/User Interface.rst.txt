User Interface
==============

Originally PySimpleGUI was used to generate the UI; old releases are using this. However, PySimpleGUI become commercial software and hence it is not appropriate to Open-Source project. 
Therefore transition was made to Kivy UI. The transition was quite cumbersome,as Kivy uses different style of UI architecture. 


Outstanding issues
------------------

Kivy is less suitable for working with multiple windows and pop-ups. Therefore multiple windows are avoided and pop-ups are done separately using tkinter Python library. 

Kivy initially caused issues with packaging LD into executable, to be used directly as an integrated button in CATIA. Therefore, currently standalone executable is not available.
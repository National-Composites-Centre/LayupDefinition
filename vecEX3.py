import numpy as np 
import os
    
def wrmmm(Multi = False):
    #Supports collection of geometry information (vecotr/point coordinates) from Catia
    #creates temporary file to export vector and point:
    #C:\Users\jk17757\Local Documents\python\TheProject\CatiaFiles\wrmmm
    #IDP_scriptsource_1902_A001_JK.wrl
    fl = open("C:\\temp\\xxx.wrl", "rt")
    flstr1 = fl.read() 
    vec = np.zeros([1,3])
    #interogates the .wrl file and creates vector data:
    # ~~~ check for when there is no vector ~~~ error handling to be added ~~~~~
    if "geometry  IndexedLineSet" in flstr1: 
        flstr = flstr1.split("geometry  IndexedLineSet")[1]
        flstr = flstr.split("[")[1]
        flstr = flstr.split("]")[0]
        p1 = flstr.split(",")[0]
        p2 = flstr.split(",")[1]
        x1 = float(p1.split(" ")[1])
        y1 = float(p1.split(" ")[2])
        z1 = float(p1.split(" ")[3])
        x2 = float(p2.split(" ")[1])
        y2 = float(p2.split(" ")[2])
        z2 = float(p2.split(" ")[3])
        vec[0,0] = x2 - x1
        vec[0,1] = y2 - y1
        vec[0,2] = z2 - z1
    
    #interogates the .wrl file and creates point data:
    # ~~~ more error handling required ~~~ what if multiple points are present... etc..~~~~~
    if Multi == False:
        f_point = np.zeros([1,3])
        if "geometry PointSet" in flstr1: 
            flstr = flstr1.split("geometry PointSet")[1]
            flstr = flstr.split("[")[1]
            flstr = flstr.split("]")[0]
            p1 = flstr.split(",")[0]
            f_point[0,0] = float(p1.split(" ")[1])
            f_point[0,1] = float(p1.split(" ")[2])
            f_point[0,2] = float(p1.split(" ")[3])
    elif Multi == True:
        cnt = flstr1.count("geometry PointSet")
        f_point = np.zeros([cnt,3])
        i = 0
        while i < cnt:
            flstr = flstr1.split("geometry PointSet")[i+1]
            flstr = flstr.split("[")[1]
            flstr = flstr.split("]")[0]
            p1 = flstr.split(",")[0]
            f_point[i,0] = float(p1.split(" ")[1])
            f_point[i,1] = float(p1.split(" ")[2])
            f_point[i,2] = float(p1.split(" ")[3])
            i = i + 1
    
    #closes the .wrl file
    fl.close()
    #~~~~~the remove should have "finally" clause, needs to always remove the file or next sim will fail~~~~
    os.remove("C:\\temp\\xxx.wrl")
    #print(f_point,"f_point")
    return(vec, f_point)
    
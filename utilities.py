
import numpy as np
from numpy.linalg import norm
import math


def sharpness(mat_list):
    print("mat_list")
    print(mat_list)

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




#test

#mat_list = np.asarray([[1,2,3],[1,3,3],[1,4,3],[1,5,3],[3,5,3]])
#test = sharpness(mat_list)
#print(test)
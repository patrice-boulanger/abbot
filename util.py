#!/usr/bin/env python

import math

def fequals(a, b, tolerance = 0.000001):
    """ Returns true if a (almost) equals b according to the given tolerance """
    return (a - tolerance <= b) and (a + tolerance >= b) 

def intercept2d(x0, y0, x1, y1, y, precision = 6):
    """ Apply the intercept theorem (Thales) in 2D """
    return round(x0 + (x1 - x0) * (y - y0) / (y1 - y0), precision) 
   
def colinear2d(x0, y0, x1, y1, x2, y2):
    """ Returns true if three 2d points are colinear """
    
    u, v = [ x1 - x0, y1 - y0 ], [ x2 - x0, y2 - y0 ]
    
    ulen = math.sqrt(u[0] * u[0] + u[1] * u[1])
    vlen = math.sqrt(v[0] * v[0] + v[1] * v[1])
    
    if fequals(ulen, 0) or fequals(vlen, 0):
        return True
    
    u1, v1 = [ u[0] / ulen, u[1] / ulen ], [ v[0] / vlen, v[1] / vlen ]
    
    return fequals(1, abs(u1[0] * v1[0] + u1[1] * v1[1]))

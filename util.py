#!/usr/bin/env python

def fequals(a, b, tolerance = 0.000001):
    """ Returns true if a (almost) equals b according to the given tolerance """
    return (a - tolerance <= b) and (a + tolerance >= b) 

def intercept2d(x0, y0, x1, y1, y, precision = 6):
    """ Apply the intercept theorem (Thales) in 2D """
    return round(x0 + (x1 - x0) * (y - y0) / (y1 - y0), precision) 
   

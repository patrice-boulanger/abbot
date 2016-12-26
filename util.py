#!/usr/bin/env python

def fequals(a, b, tolerance = 0.000001):
    return (a - tolerance <= b) and (a + tolerance >= b) 

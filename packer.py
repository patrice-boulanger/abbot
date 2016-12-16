#!/usr/bin/env python

import sys

class Rectangle:

    def __init__(self):
        self.x = self.y = 0
        self.w = self.h = 0

    def __init__(self, w, h):
        self.x = self.y = 0
        self.w = w
        self.h = h
                
    def area(self):
        return self.w * self.h

class Packer:
    """ A class which packs rectangles on a surface """

    def __init__(self, config):
        """ Initialize the surface """

        # Dimensions of the printer plate
        self.xmax = self.config["printer"]["max"][0]
        self.ymax = self.config["printer"]["max"][1]

        # List of rectangles to pack
        self.rects = []
                
    def add(self, width, length):
        self.rects.append( Rectangle(width, height) )

    def arrange(self):

        # Reverse sort the rectangles according the longest dimension
        self.rects.sort(reverse = True, key = lambda r: max(r.w, r.h))
        
        positions = []

        for r in self.rects:

            if len(positions) == 0:
                if r[0] <= self.xmax and r[1] <= self.ymax:
                    positions.append( (0, 0) )
                    continue
                else:
                    print("no space left on plate", file = sys.stderr)
            

#!/usr/bin/env python

import sys
from model import Model

class Rectangle:
    """ A simple 2D rectangle """

    def __init__(self):
        self.x = self.y = 0
        self.w = self.h = 0

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class Packer:
    """ A class which packs models on a surface """

    def __init__(self, config):
        """ Initialize the surface """

        self.config = config
        
        # Dimensions of the printer plate
        self.xmax = self.config["printer"]["max"][0]
        self.ymax = self.config["printer"]["max"][1]

        # List of models to pack
        self.models = []
        # List of busy places
        self.places = []
        
    def add(self, model):
        self.models.append(model)

    def arrange(self):
        # Reverse sort the rectangles according their longest dimension
        self.models.sort(reverse = True, key = lambda m: max(m.bbox_max[0] - m.bbox_min[0], m.bbox_max[1] - m.bbox_min[1]))

        a_width, a_height = 0, 0
        gap = 10
        
        for m in self.models:
            
            m_width = m.bbox_max[0] - m.bbox_min[0]
            m_height = m.bbox_max[1] - m.bbox_min[1]

            # If the plate is empty, just try to put the first model
            if len(self.places) == 0:
                if m_width <= self.xmax and m_height <= self.ymax:
                    self.places.append( Rectangle(0, 0, m_width, m_height) )
                    a_width = m_width
                    a_height = m_height
                    continue
                else:
                    print("Model doesn't fit on the plate", file = sys.stderr)
                    return False

            if a_width <= a_height and a_width + m_width <= self.xmax:
                self.places.append( Rectangle(gap + self.places[-1].x + self.places[-1].w, self.places[-1].y, m_width, m_height) )
                a_width += m_width + gap
            elif a_height <= a_width and a_height + m_height <= self.ymax:
                self.places.append( Rectangle(self.places[-1].x, gap + self.places[-1].y + self.places[-1].h, m_width, m_height) )
                a_height += m_height + gap
            else:
                print("Model doesn't fit on the plate", file = sys.stderr)
                return False


        assert(len(self.models) == len(self.places))
        
        # Finally, center the whole busy area on the plate
        tx = (self.xmax - a_width) / 2
        ty = (self.ymax - a_height) / 2

        for m, r in zip(self.models, self.places):
            tz = -m.bbox_min[2]
            m.translate(tx + r.x + r.w / 2, ty + r.y + r.h / 2, tz)
              
        return True
            
            

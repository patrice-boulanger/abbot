#!/usr/bin/env python

import sys
from model import Model

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
                
    def add(self, model):
        self.models.append(model)

    def arrange(self):
        # Reverse sort the rectangles according the longest dimension
        self.models.sort(reverse = True, key = lambda m: max(m.bbox_max[0] - m.bbox_min[0], m.bbox_max[1] - m.bbox_min[1]))

        a_width, a_height = 0, 0
        
        for m in self.models:
            m_width = m.bbox_max[0] - m.bbox_min[0]
            m_height = m.bbox_max[1] - m.bbox_min[1]
            
            if m_width >= m_height:
                # Attempt to grow the used surface on its smallest dimension
                if a_width <= a_height:
                    if a_width + m_width < self.xmax:
                        tx = a_width + m_width
                        ty = 0
                        tz = - m.bbox_min[2] # Fit the model on the plate
                        
                        if a_width + m_width > self.xmax or a_height + m_height:
                print("cannot find a place to fit all models on the plate")
                return False

            
            

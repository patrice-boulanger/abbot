#!/usr/bin/env python3

import numpy
import stl

import model, ui

class slicer:
    """ Abbot slicer """

    config = dict()
    
    def __init__(self):
        """ Constructor """

        # Basic default configuration
        # Distance are expressed in mm and speeds in mm/s

        # Printer
        self.config["printer"] = dict()
        self.config["printer"]["min"] = [ 0, 0, 0 ]
        self.config["printer"]["max"] = [ 200, 200, 200 ]
        
        # Extruder(s)
        self.config["extruder"] = dict()
        
        self.config["extruder"]["count"] = 1

        self.config["extruder"]["0"] = dict()        
        self.config["extruder"]["0"]["diameter"] = 0.35
        self.config["extruder"]["0"]["temp"] = 200
        self.config["extruder"]["0"]["offset_x"] = 0
        self.config["extruder"]["0"]["offset_y"] = 0
        self.config["extruder"]["0"]["fan_speed"] = 255
        
        self.config["extruder"]["0"]["retract"] = dict()
        self.config["extruder"]["0"]["retract"]["speed"] = 110
        self.config["extruder"]["0"]["retract"]["distance"] = 4
                
        # Layer height
        self.config["quality"] = 0.2
        
        # Speeds
        self.config["speed"] = dict()
        self.config["speed"]["print"] = 40
        self.config["speed"]["travel"] = 150
        self.config["speed"]["first_layer"] = 30
        self.config["speed"]["outer_perimeter"] = 30
        self.config["speed"]["inner_perimeter"] = 40
        self.config["speed"]["infill"] = 60
        self.config["speed"]["skin_infill"] = 30
        
        # Infill
        self.config["thickness"] = dict()
        self.config["thickness"]["shell"] = 0.7
        self.config["thickness"]["top_bottom"] = 0.6

    def arrange(self, models):
        """ Packs models on the printer plate according to their bounding box """

        # Sort the models order by decreasing surface
        models.sort(reverse = True, key = lambda m: (m.bbox_max[0] - m.bbox_min[0]) * (m.bbox_max[1] - m.bbox_min[1]))
        # Divide the printer plate into a list of areas (X offset, Y offset, width, height),
        # Initialized at 90% of the size of the plate
        areas = [ [0, 0, 0.9 * self.config["printer"]["max"][0], 0.9 * self.config["printer"]["max"][1]] ]

        gap = 10 # Minimum gap betweem 2 models
        
        for t in models:
            tx = -t.bbox_min[0]
            ty = -t.bbox_min[1]
            tz = -t.bbox_min[2] # Force the model to lay on the plate
            
            w = gap + (t.bbox_max[0] - t.bbox_min[0])
            h = gap + (t.bbox_max[1] - t.bbox_min[1])

            # Try to populate smallest areas first
            areas.sort(key = lambda p: p[2] * p[3])

            for a in areas:
                if w <= a[2] and h <= a[3]:
                    tx += a[0] + gap
                    ty += a[1] + gap

                    na1 = [ a[0] + w, a[1]    , a[2] - w, h ]
                    na2 = [ a[0]    , a[1] + h, a[2]    , a[3] - h]

                    areas.remove(a)
                    if na1[2] != 0 and na1[3] != 0:
                        areas.append(na1)
                    if na2[2] != 0 and na2[3] != 0:
                        areas.append(na2)
                    
                    break
                    
            if tx == -1 or ty == -1:
                print(t.name + " doesn't fit on the plate")
                return

            t.translate(tx, ty, tz)

        # Center the models on the Y axis
        for a in areas:
            if a[2] == 0.9 * self.config["printer"]["max"][0]:
                ty = a[3] / 2
                for m in models:
                    m.translate(0, ty, 0)            
        
    def run(self):
        """ Slicer main loop """

        verbose = self.config["verbose"]
        models = []
        
        # Load models
        for m in self.config["models"]:
            try:
                mdl = model.model(m, stl.mesh.Mesh.from_file(m))
                models.append(mdl)
                
            except Exception as err:
                print(str(err))
                return

        self.arrange(models)

        

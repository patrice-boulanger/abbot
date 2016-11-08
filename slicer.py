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

        # Packs models on the printer plate according to their bounding box
        models.sort(reverse = True, key = lambda m: (m.bbox_max[0] - m.bbox_min[0]) * (m.bbox_max[1] - m.bbox_min[1]))
        # Divide the printer plate into a List of sub-plates (X offset, Y offset, width, height), initialized to the full plate
        plates = [ [0, 0, self.config["printer"]["max"][0], self.config["printer"]["max"][1]] ]

        for t in models:
            print("processing " + t.name)

            offx = offy = -1
            w = t.bbox_max[0] - t.bbox_min[0]
            h = t.bbox_max[1] - t.bbox_min[1]

            plates.sort(key = lambda p: p[2] * p[3])

            for p in plates:
                if w <= p[2] and h <= p[3]:
                    offx = p[0]
                    offy = p[1]

                    np1 = [ p[0] + w, p[1]    , p[2] - w, h ]
                    np2 = [ p[0]    , p[1] + h, p[2]    , p[3] - h]

                    plates.remove(p)
                    plates.append(np1)
                    plates.append(np2)
                    
                    break
                    
            if offx == -1 or offy == -1:
                print(t.name + " doesn't fit on the plate")
                return

            print("move " + t.name + " to " + str(offx) + "," + str(offy))
            t.translate(offx, offy, 0)

        for p in plates:
            print(str(p))
            
        msh = []
        for m in models:
            msh.append(m.mesh)
            
        ui.show_mesh(msh)

#!/usr/bin/env python3

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
        print(self.config)

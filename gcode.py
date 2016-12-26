#!/usr/bin/env python

import os, math, sys
import numpy as np

class GCode:
    
    def __init__(self, config):
        self.config = config
        self.fd = None
                
        # Convert speed from mm/s to mm/min
        self.sp_travel = self.config["speed"]["travel"] * 60
        self.sp_print = self.config["speed"]["print"] * 60
        
        # Areas to compute extrusion length
        self.nozzle_area = self.config["extruder"]["nozzle_diameter"] * self.config["extruder"]["nozzle_diameter"] * math.pi
        self.filament_area = self.config["extruder"]["filament_diameter"] * self.config["extruder"]["filament_diameter"] * math.pi

        # List of commands
        self.lineno = 1
        
    def emit(self, text):
        print(text)
        self.lineno = self.lineno + 1
        
    def extrusion_length(self, x0, y0, x1, y1):
        """ Returns the extrusion length to print from (x0, y0) to (x1, y1) """

        dx, dy = x0 - x1, y0 - y1
        distance = math.sqrt((dx * dx) + (dy * dy))
        length = (self.nozzle_area * distance) / self.filament_area

        return length
        
    def dump(self, layers):
        
        if self.config["verbose"]:
            print("G-Code commands", file = sys.stderr)
            
        z_incr = self.config["quality"]
        z_max = len(layers) * z_incr

        # Last point
        prev = [ None, None ]
        # Extrusion length
        e_len = 0
        # Layer index
        layer_nr = 0 
        
        for z in np.arange(0.0, z_max, z_incr):
            layer = layers[layer_nr]

            self.emit("; layer #" + str(layer_nr))
            for path in layer:
                self.emit("G0 F{0} X{1:.8} Y{2:.8} Z{3:.8}".format(self.sp_travel, path[0][0], path[0][1], z + z_incr))
                    
                e_len += self.extrusion_length(path[0][0], path[0][1], path[1][0], path[1][1])

                self.emit("G1 F{0} X{1:.8} Y{2:.8} E{3:.12}".format(self.sp_print, path[1][0], path[1][1], e_len))
                prev[0], prev[1] = path[1][0], path[1][1]
                        
                for p in path[2:]:
                    e_len += self.extrusion_length(prev[0], prev[1], p[0], p[1])
                            
                    self.emit("G1 X{0:.8} Y{1:.8} E{2:.12}".format(p[0], p[1], e_len))
                    prev[0], prev[1] = p[0], p[1]
                            
            layer_nr += 1

#!/usr/bin/env python

import os, math, sys
import numpy as np
from timeit import default_timer as timer

from fill import GridPattern

class GCode:
    
    def __init__(self, config):
        self.config = config
        self.fd = None
                
        # Convert speed from mm/s to mm/min
        self.sp_travel = self.config["speed"]["travel"] * 60
        self.sp_print = self.config["speed"]["print"] * 60
        self.sp_infill = self.config["speed"]["infill"] * 60
        
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
    
    def do_path(self, path, z, length):
        """ Emits the gcode for the specified path, returns the length of filament extruded """

        # Current extrusion length
        e_len = length
        # Last point
        prev = [ None, None ]

        self.emit("G0 F{0} X{1:.5f} Y{2:.5f} Z{3:.5f}".format(self.sp_travel, path[0][0], path[0][1], z + float(self.config["quality"])))
                  
        e_len += self.extrusion_length(path[0][0], path[0][1], path[1][0], path[1][1])
        self.emit("G1 F{0} X{1:.5f} Y{2:.5f} E{3:.5f}".format(self.sp_print, path[1][0], path[1][1], e_len))
        
        prev[0], prev[1] = path[1][0], path[1][1]
        
        for p in path[2:]:
            e_len += self.extrusion_length(prev[0], prev[1], p[0], p[1])            
            self.emit("G1 X{0:.5f} Y{1:.5f} E{2:.5f}".format(p[0], p[1], e_len))
            prev[0], prev[1] = p[0], p[1]

        return e_len
    
    def dump(self, layers):
        
        if self.config["verbose"]:
            print("Dump G-Code ...", end = "", file = sys.stderr)
            sys.stderr.flush()
            
        z_incr = self.config["quality"]
        z_max = len(layers) * z_incr

        # Extrusion length
        e_len = 0
        # Layer index
        layer_nr = 0 

        start = timer()        

        # Grid pattern with step == 1mm

        for z in np.arange(0.0, z_max, z_incr):
            layer = layers[layer_nr]
            self.emit("; layer #" + str(layer_nr))
            
            for paths in layer:
                xmin = 9999
                ymin = 9999
                xmax = 0
                ymax = 0

                # Perimeter
                for path in paths:
                    for p in path:
                        xmin = min(xmin, p[0])
                        xmax = max(xmax, p[0])
                        ymin = min(ymin, p[1])
                        ymax = max(ymax, p[1])

                    self.emit("; perimeter")
                    e_len = self.do_path(path, z, e_len)

                # Filling
                self.emit("; infill")
                    
                if layer_nr < 3 or layer_nr > len(layers) - 4:
                    step = self.config["extruder"]["nozzle_diameter"]
                else:
                    step = 1
                        
                grid = GridPattern(xmin, ymin, xmax, ymax, step) 

                grid.scan(paths, layer_nr % 2)
                for s in grid.segments:
                    self.emit("G0 F{0} X{1:.5f} Y{2:.5f}".format(self.sp_infill, s[0], s[1]))
                    e_len += self.extrusion_length(s[0], s[1], s[2], s[3])
                    self.emit("G1 F{0} X{1:.5f} Y{2:.5f} E{3:.5f}".format(self.sp_infill, s[2], s[3], e_len))
                    
            layer_nr += 1

        end = timer()

        if self.config["verbose"]:
            print(" done in {0:3.2f}s, {1:.2f}mm extruded".format(end - start, e_len), file = sys.stderr)
            sys.stderr.flush()
            

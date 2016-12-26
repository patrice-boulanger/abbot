#!/usr/bin/env python

import math, sys
import numpy as np

class Optimizer:
    """ """

    def __init__(self, config):
        """ Constructor """
        self.config = config

    def colinear(self, p0, p1, p2):
        """ Returns true if three 2d points are colinear """
        
        u, v = [ p1[0] - p0[0], p1[1] - p0[1] ], [ p2[0] - p0[0], p2[1] - p0[1] ]

        ulen = math.sqrt(u[0] * u[0] + u[1] * u[1])
        vlen = math.sqrt(v[0] * v[0] + v[1] * v[1])

        if np.isclose(ulen, 0) or np.isclose(vlen, 0):
            return True
        
        u1, v1 = [ u[0] / ulen, u[1] / ulen ], [ v[0] / vlen, v[1] / vlen ]
        
        return np.isclose(1, abs(u1[0] * v1[0] + u1[1] * v1[1]))
    
    def points_from_segments(self, segs):
        """ Take a list of segments and organize them into one or several continuous lists of points """

        paths = []

        while len(segs) > 0:
            # List of tuples
            path = [] # [ (x,y), (x,y), ... (x,y) ]
            
            # Initialize the path with the 2 first points
            path.append((segs[0][0], segs[0][1]))
            path.append((segs[0][2], segs[0][3]))
                
            del segs[0]

            idx = 0
            while len(segs) > 0 and idx < len(segs):
                s = segs[idx] # (xa, ya, xb, yb)
                
                if np.isclose(path[0][0], s[0]) and np.isclose(path[0][1], s[1]):
                    if self.colinear(path[0], path[1], (s[2], s[3])):
                        path[0] = (s[2], s[3])
                    else:
                        path.insert(0, (s[2], s[3]))
                        
                    del segs[idx]
                    idx = -1
                elif np.isclose(path[0][0], s[2]) and np.isclose(path[0][1], s[3]):
                    if self.colinear(path[0], path[1], (s[0], s[1])):
                        path[0] = (s[0], s[1])
                    else:
                        path.insert(0, (s[0], s[1]))
                        
                    del segs[idx]
                    idx = -1
                elif np.isclose(path[-1][0], s[0]) and np.isclose(path[-1][1], s[1]):
                    if self.colinear(path[-2], path[-1], (s[2], s[3])):
                        path[-1] = (s[2], s[3])
                    else:
                        path.append((s[2], s[3]))
                        
                    del segs[idx]
                    idx = -1
                elif np.isclose(path[-1][0], s[2]) and np.isclose(path[-1][1], s[3]):
                    if self.colinear(path[-2], path[-1], (s[0], s[1])):
                        path[-1] = (s[0], s[1])
                    else:
                        path.append((s[0], s[1]))
                        
                    del segs[idx]
                    idx = -1
                    
                idx = idx + 1

            if len(path) > 1:
                paths.append(path)
            else:
                print("path of length == 1")

        return paths
        
    def optimize(self, layers):

        if self.config["verbose"]:
            print("Optimization", file = sys.stderr)
        
        # Number of segments in the slicing plan before optimization
        ini_sz = 0
        # Number of points in the final slicing plan
        new_sz = 0
        # Optimized layers
        opt_layers = []

        for segs in layers:
            ini_sz += len(segs) 
            plist = self.points_from_segments(segs)
            new_sz += len(plist)
            
            opt_layers.append(plist)
            
        if self.config["verbose"]:
            print(" {0} segments ({1} points) -> {2} points ({3:.1f}%)".format(ini_sz, 2 * ini_sz, new_sz, (new_sz * 100 / ini_sz) - 100),
                  file = sys.stderr)

        return opt_layers

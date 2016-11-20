#!/usr/bin/env python

import math

class Optimizer:
    """ """

    def __init__(self, config):
        """ Constructor """
        self.config = config

    def colinear(self, v0, v1, v2):
        """ Returns true if three 2d points are colinear """
        
        a, b = [ v0[0] - v1[0], v0[1] - v1[1] ], [ v0[0] - v2[0], v0[1] - v2[1] ]

        la = math.sqrt(a[0]*a[0] + a[1]*a[1])
        lb = math.sqrt(b[0]*b[0] + b[1]*b[1])

        a1, b1 = [ a[0] / la, a[1] / la ], [ b[0] / lb, b[1] / lb ]
        
        return abs(a1[0]*b1[0] + a1[1]*b1[1]) == 1
    
    def points_from_segments(self, segs):
        """ Take a list of segments and organize them into one or several continuous list of points """
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
                
                if path[0] == (s[0], s[1]):
                    if self.colinear(path[0], path[1], (s[2], s[3])):
                        path[0] = (s[2], s[3])
                    else:
                        path.insert(0, (s[2], s[3]))
                        
                    del segs[idx]
                    idx = -1
                elif path[0] == (s[2], s[3]):
                    if self.colinear(path[0], path[1], (s[0], s[1])):
                        path[0] = (s[0], s[1])
                    else:
                        path.insert(0, (s[0], s[1]))
                        
                    del segs[idx]
                    idx = -1
                elif path[-1] == (s[0], s[1]):
                    if self.colinear(path[-2], path[-1], (s[2], s[3])):
                        path[-1] = (s[2], s[3])
                    else:
                        path.append((s[2], s[3]))
                        
                    del segs[idx]
                    idx = -1
                elif path[-1] == (s[2], s[3]):
                    if self.colinear(path[-2], path[-1], (s[0], s[1])):
                        path[-1] = (s[0], s[1])
                    else:
                        path.append((s[0], s[1]))
                        
                    del segs[idx]
                    idx = -1
                
                idx = idx + 1

            paths.append(path)

        return paths
        
    def optimize(self, layers):

        if self.config["verbose"]:
            print("Start optimization")
        
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
            print(" {0} segments ({1} points) -> {2} points ({3:.1f}%)".format(ini_sz, 2 * ini_sz, new_sz, (new_sz * 100 / ini_sz) - 100))

        return opt_layers

#!/usr/bin/env python

import math, sys
import numpy as np
from timeit import default_timer as timer

from util import fequals, colinear2d

class Optimizer:
    """ """

    def __init__(self, config):
        """ Constructor """
        self.config = config
        
    def points_from_segments(self, segs):
        """ Take a list of segments and organize them into one or several continuous lists of points.
            If several successive points are aligned, reduced the number of points keeping only the endpoints. """

        paths = []

        while len(segs) > 0:
            # List of tuples
            path = [] # [ (x,y), (x,y), ... (x,y) ]
            
            # Initialize the path with the 2 first points
            assert(not fequals(segs[0][0], segs[0][2]) or not fequals(segs[0][1], segs[0][3]))

            path.append((segs[0][0], segs[0][1]))
            path.append((segs[0][2], segs[0][3]))

            del segs[0]            

            idx = 0
            while len(segs) > 0 and idx < len(segs):
                s = segs[idx] # (xa, ya, xb, yb)
                
                if fequals(path[0][0], s[0]) and fequals(path[0][1], s[1]):
                    if colinear2d(path[0][0], path[0][1], path[1][0], path[1][1], s[2], s[3]):
                        path[0] = (s[2], s[3])
                    else:
                        path.insert(0, (s[2], s[3]))
                        
                    del segs[idx]
                    idx = -1
                elif fequals(path[0][0], s[2]) and fequals(path[0][1], s[3]):
                    if colinear2d(path[0][0], path[0][1], path[1][0], path[1][1], s[0], s[1]):
                        path[0] = (s[0], s[1])
                    else:
                        path.insert(0, (s[0], s[1]))
                        
                    del segs[idx]
                    idx = -1
                elif fequals(path[-1][0], s[0]) and fequals(path[-1][1], s[1]):
                    if colinear2d(path[-2][0], path[-2][1], path[-1][0], path[-1][1], s[2], s[3]):
                        path[-1] = (s[2], s[3])
                    else:
                        path.append((s[2], s[3]))
                        
                    del segs[idx]
                    idx = -1
                elif fequals(path[-1][0], s[2]) and fequals(path[-1][1], s[3]):
                    if colinear2d(path[-2][0], path[-2][1], path[-1][0], path[-1][1], s[0], s[1]):
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
        """ At this point, the layers are a list of unordered segments.
            The optimisation process has to organized them into a list of successive points
            that draw the paths to drive the tool. 
            This process also removes duplicated points and build longer segments when several 
            points are colinear. """
        
        if self.config["verbose"]:
            print("Optimization ... ", file = sys.stderr)
            sys.stderr.flush()
            
        # Number of segments in the slicing plan before optimization
        ini_sz = 0
        # Number of points in the final slicing plan
        new_sz = 0
        # Optimized layers
        optimized = []

        cnt = 0
        
        start = timer()

        for slice in layers:

            paths = []
            
            for segs in slice:
            
                if self.config["verbose"]:
                    print(" {:3.2f}%".format(cnt / len(layers) * 100.0), end = "", file = sys.stderr)
                    print("\b\b\b\b\b\b\b\b", end = "", file = sys.stderr)
                    sys.stderr.flush()
            
                ini_sz += len(segs) 
                plist = self.points_from_segments(segs)            
                new_sz += len(plist)

                paths.append(plist)

            optimized.append(paths)
            
            cnt += 1
            
        end = timer()
            
        if self.config["verbose"]:
            print(" {0} segments ({1} points) -> {2} points ({3:.1f}% in {4:.2f}s)".format(ini_sz,
                                                                                          2 * ini_sz,
                                                                                          new_sz,
                                                                                          (new_sz * 100 / ini_sz) - 100,
                                                                                          end - start),
                  file = sys.stderr)
            sys.stderr.flush()

        return optimized

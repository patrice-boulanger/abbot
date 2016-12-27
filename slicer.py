#!/usr/bin/env python

import sys
import numpy as np
import stl
from timeit import default_timer as timer

from packer import Packer
from model import Model
from util import fequals

class Slicer:

    def __init__(self, config, models):
        """ Constructor """
        self.config = config
        self.models = models
        
    def arrange(self):
        """ Packs models on the printer plate according to their bounding box """
        
        if self.config["verbose"]:
            print(" Arrange models on the plate ...", file = sys.stderr, end = "")
            sys.stderr.flush()

        packer = Packer(self.config)
            
        start = timer()
        
        for m in self.models:
            packer.add(m)

        if not packer.arrange():
            return
            
        end = timer()

        if self.config["verbose"]:
            print(" done ({0:.2}s)".format(end - start), file = sys.stderr)

                    
    def intercept2d(self, x0, y0, x1, y1, y, precision = 8):
        """ Apply the intercept theorem in 2D """
        return round(x0 + (x1 - x0) * (y - y0) / (y1 - y0), precision) 
   
    def slice_facet(self, facet, z):
        """ Slice a facet at height z """

        # Coordinates of the resulting segment
        p = [ [None, None], [None, None] ]
        n = 0
        
        # Vertices of the facet
        v0 = [ facet[0], facet[1], facet[2] ]
        v1 = [ facet[3], facet[4], facet[5] ]
        v2 = [ facet[6], facet[7], facet[8] ]

        # Check if the facet is plane
        if fequals(v0[2], z) and fequals(v1[2], z) and fequals(v2[2], z):
            return 0, None, None, None, None        
        
        # If 2 vertices of the facet are in the slicing plan, add the edge
        if fequals(v0[2], z) and fequals(v1[2], z):
            p[0][0], p[0][1], p[1][0], p[1][1] = v0[0], v0[1], v1[0], v1[1]
            n = 2
        elif fequals(v0[2], z) and fequals(v2[2], z):
            p[0][0], p[0][1], p[1][0], p[1][1] = v0[0], v0[1], v2[0], v2[1]
            n = 2
        elif fequals(v1[2], z) and fequals(v2[2], z):
            p[0][0], p[0][1], p[1][0], p[1][1] = v1[0], v1[1], v2[0], v2[1]
            n = 2
        else:
            # Compute distance between the slicing plan and each vertex
            dv0, dv1, dv2 = v0[2] - z, v1[2] - z, v2[2] - z

	    # Slicing plan intersects the triangle
	    # Check which edge of the triangle intersects the plan and use the interception theorem
	    # to interpolate the coordinates            
            if dv0 * dv1 < 0:
                p[n][0] = self.intercept2d(v0[0], v0[2], v1[0], v1[2], z)
                p[n][1] = self.intercept2d(v0[1], v0[2], v1[1], v1[2], z)
                n += 1

            if dv1 * dv2 < 0:
                p[n][0] = self.intercept2d(v1[0], v1[2], v2[0], v2[2], z)
                p[n][1] = self.intercept2d(v1[1], v1[2], v2[1], v2[2], z)
                n += 1

            if dv0 * dv2 < 0:
                p[n][0] = self.intercept2d(v0[0], v0[2], v2[0], v2[2], z)
                p[n][1] = self.intercept2d(v0[1], v0[2], v2[1], v2[2], z)
                n += 1
                
	    # We still have to check if one of the vertices intersects the slicing plan.
	    # If yes, this is the last point of our segment, the other point has been
	    # filled at the previous step.
            if n == 1:
                if fequals(v0[2], z):
                    p[n][0], p[n][1] = v0[0], v0[1]
                    n += 1
                if fequals(v1[2], z):
                    p[n][0], p[n][1] = v1[0], v1[1]
                    n += 1
                if fequals(v2[2], z):
                    p[n][0], p[n][1] = v2[0], v2[1]
                    n += 1
                    
        return n, p[0][0], p[0][1], p[1][0], p[1][1]
    
    def build_slicing_plan(self):
        """ Slices the whole scene, returns a list of layers. Each slice is a list of unorganized segments """

        verbose = self.config["verbose"]

        if verbose:
            print("Slicing", file = sys.stderr)

        self.arrange()

        # Maximal Z slicing value 
        z_max = 0.0
        
        for m in self.models:
            if z_max < m.bbox_max[2]:
                z_max = m.bbox_max[2]

        z_incr = float(self.config["quality"])
        
        if verbose:
            print(" Slicing height is " + str(z_max) + "mm", file = sys.stderr)
            
        # Slicing loop
        slices = []

        start_loop = timer()
        for z in np.arange(0, z_max, z_incr):

            slice = []
            
            for m in self.models:
                if self.config["verbose"]:
                    print(" {:3.2f}%".format(z / z_max * 100.0), end = "", file = sys.stderr)
                    print("\b\b\b\b\b\b\b\b", end = "", file = sys.stderr)
                    sys.stderr.flush()
                
                m.set_slicing_plan(z)

                segs = []
                
                for facet in m.lst_intersect:
                    (n, xa, ya, xb, yb) = self.slice_facet(facet, z)
                    
                    if n == 2:
                        if not fequals(xa, xb) or not fequals(ya, yb):
                            segs.append((xa, ya, xb, yb))
                    else:
                        continue
                    
                if len(segs) > 0:
                    slice.append(segs)

            slices.append(slice)
                    
        end_loop = timer()
                    
        if verbose:
            print(" {0} layers extracted ({1:.2}s)".format(len(slices), end_loop - start_loop), file = sys.stderr)

        return slices


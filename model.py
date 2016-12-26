#!/usr/bin/env python

import sys, stl
import numpy as np

class Model:
        
    def __init__(self, name):
        """ Constructor, load data from file """
        self.name = name

        if self.name.lower().endswith(".stl"):
            self.mesh = stl.mesh.Mesh.from_file(self.name)
        else:
            raise ValueError("unknown model file format")
        
        # models bounds
        self.bbox_min = [ None, None, None ]
        self.bbox_max = [ None, None, None ]
        self.update_bounds()

        self.lst_intersect = [] # facets that intersect the slicing plan

    def translate(self, tx, ty, tz):
        """ Translate the mesh """
        items = [ [0, 3, 6],  # x
                  [1, 4, 7],  # y
                  [2, 5, 8] ] # z

        for p in self.mesh.points:
            for i in range(3):
                if tx != 0:
                    p[items[0][i]] += tx
                if ty != 0:
                    p[items[1][i]] += ty
                if tz != 0:
                    p[items[2][i]] += tz

        if tx != 0 or ty != 0 or tz != 0:
            self.update_bounds()
            
    def update_bounds(self):
        """ Computes model bounds """

        self.bbox_min[0] = self.bbox_min[1] = self.bbox_min[2] = 99999.0
        self.bbox_max[0] = self.bbox_max[1] = self.bbox_max[2] = -1.0
        
        for p in self.mesh.points:
            # p contains (x, y, z)
            self.bbox_max[0] = max(p[stl.Dimension.X], self.bbox_max[0])
            self.bbox_min[0] = min(p[stl.Dimension.X], self.bbox_min[0])
            self.bbox_max[1] = max(p[stl.Dimension.Y], self.bbox_max[1])
            self.bbox_min[1] = min(p[stl.Dimension.Y], self.bbox_min[1])
            self.bbox_max[2] = max(p[stl.Dimension.Z], self.bbox_max[2])
            self.bbox_min[2] = min(p[stl.Dimension.Z], self.bbox_min[2])
        
    def set_slicing_plan(self, z):
        """ Compute internal list of facets that intersect w/ the slicing plan """

        del self.lst_intersect[:]
        
        for p in self.mesh.points:
            zmin = min(p[2], min(p[5], p[8]))
            zmax = max(p[2], max(p[5], p[8]))

            if zmin <= z and zmax >= z:
                self.lst_intersect.append(p)

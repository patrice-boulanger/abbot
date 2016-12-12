#!/usr/bin/env python

import stl

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
        self.lst_above = [] # facets above the slicing plan

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

        self.bbox_min[0] = self.bbox_max[0] = stl.Dimension.X
        self.bbox_min[1] = self.bbox_max[1] = stl.Dimension.Y
        self.bbox_min[2] = self.bbox_max[2] = stl.Dimension.Z
        
        for p in self.mesh.points:
            # p contains (x, y, z)
            self.bbox_max[0] = max(p[stl.Dimension.X], self.bbox_max[0])
            self.bbox_min[0] = min(p[stl.Dimension.X], self.bbox_min[0])
            self.bbox_max[1] = max(p[stl.Dimension.Y], self.bbox_max[1])
            self.bbox_min[1] = min(p[stl.Dimension.Y], self.bbox_min[1])
            self.bbox_max[2] = max(p[stl.Dimension.Z], self.bbox_max[2])
            self.bbox_min[2] = min(p[stl.Dimension.Z], self.bbox_min[2])
        
    def set_slicing_plan(self, z):
        """ Compute internal list of facets for the given slicing plan """

        idx = 0
        
        for p in self.mesh.points:
            zmin = min(p[2], min(p[5], p[8]))
            zmax = max(p[2], max(p[5], p[8]))

            if zmin <= z and zmax >= z:
                self.lst_intersect.append(idx)
            elif zmin > z:
                self.lst_above.append(idx)
            else:
                print("facet " + idx + " of model " + self.name + " is under initial slicing plan, it will be ignored")
                
            idx += 1

    def update_slicing_plan(self, z):
        """ Update list of facets according to the new slicing plan """

        # First, remove facet that are now under the new slicing plan
        nlst = []
        
        for p in self.lst_intersect:            
            facet = self.mesh.points[p]
            zmax = max(facet[2], max(facet[5], facet[8]))

            if z <= zmax:
                nlst.append(p)

        self.lst_intersect = nlst

        # Then, look for facets that now intersect with the new slicing plan
        nlst2 = []
        
        for p in self.lst_above:            
            facet = self.mesh.points[p]
            zmin = min(facet[2], min(facet[5], facet[8]))
        
            if z >= zmin:
                self.lst_intersect.append(p)
            else:
                nlst2.append(p)

        self.lst_above = nlst2

#!/usr/bin/env python3

import stl

class model:
        
    def __init__(self, name, mesh):
        """ Constructor, takes numpy STL data as argument """

        print("Create model from " + name)
        
        self.name = name
        self.mesh = mesh

        # models bounds
        self.bbox_min = [ None, None, None ]
        self.bbox_max = [ None, None, None ]
        
        # computes model bounds
        self.update_bounds()

        # align the mesh to (0,0,0)
        tx = ty = tz = 0

        if self.bbox_min[0] != 0:
            tx = -self.bbox_min[0]

        if self.bbox_min[1] != 0:
            ty = -self.bbox_min[1]

        if self.bbox_min[2] != 0:
            tz = -self.bbox_min[2]

        if tx != 0 or ty != 0 or tz != 0:
            print(" translated to (" + str(tx) + "," + str(ty) + "," + str(tz) + ")")
            self.translate(tx, ty, tz)

        self.bbox_min[0] += tx
        self.bbox_max[0] += tx
        self.bbox_min[1] += ty
        self.bbox_max[1] += ty
        self.bbox_min[2] += tz
        self.bbox_max[2] += tz
        
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
        """ Computes models bounds """

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
        

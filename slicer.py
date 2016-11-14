#!/usr/bin/env python3

# Numpy
import numpy as np
import stl
# Abbot
import model, ui, gcode

class Slicer:
    """ Abbot slicer """

    config = dict()
    
    def __init__(self):
        """ Constructor """

        # Basic default configuration
        # Distance are expressed in mm and speeds in mm/s

        # Printer
        self.config["printer"] = dict()
        self.config["printer"]["gcode"] = "marlin"
        self.config["printer"]["min"] = [ 0, 0, 0 ]
        self.config["printer"]["max"] = [ 200, 200, 200 ]
        
        # Extruder(s)
        self.config["extruder"] = dict()
        
        self.config["extruder"]["count"] = 1

        self.config["extruder"]["0"] = dict()        
        self.config["extruder"]["0"]["nozzle_diameter"] = 0.35
        self.config["extruder"]["0"]["filament_diameter"] = 1.75 
        self.config["extruder"]["0"]["temperature"] = 200
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

    def arrange(self, models):
        """ Packs models on the printer plate according to their bounding box """

        # Sort the models order by decreasing surface
        models.sort(reverse = True, key = lambda m: (m.bbox_max[0] - m.bbox_min[0]) * (m.bbox_max[1] - m.bbox_min[1]))
        # Divide the printer plate into a list of areas (X offset, Y offset, width, height),
        # Initialized at 90% of the size of the plate
        areas = [ [0, 0, 0.9 * self.config["printer"]["max"][0], 0.9 * self.config["printer"]["max"][1]] ]

        gap = 10 # Minimum gap betweem 2 models
        
        for t in models:
            tx = -t.bbox_min[0]
            ty = -t.bbox_min[1]
            tz = -t.bbox_min[2] # Force the model to lay on the plate
            
            w = gap + (t.bbox_max[0] - t.bbox_min[0])
            h = gap + (t.bbox_max[1] - t.bbox_min[1])

            # Try to populate smallest areas first
            areas.sort(key = lambda p: p[2] * p[3])

            for a in areas:
                if w <= a[2] and h <= a[3]:
                    tx += a[0] + gap
                    ty += a[1] + gap

                    na1 = [ a[0] + w, a[1]    , a[2] - w, h ]
                    na2 = [ a[0]    , a[1] + h, a[2]    , a[3] - h]

                    areas.remove(a)
                    if na1[2] != 0 and na1[3] != 0:
                        areas.append(na1)
                    if na2[2] != 0 and na2[3] != 0:
                        areas.append(na2)
                    
                    break
                    
            if tx == -1 or ty == -1:
                print(t.name + " doesn't fit on the plate")
                return

            t.translate(tx, ty, tz)

        # Center the models on the Y axis
        for a in areas:
            if a[2] == 0.9 * self.config["printer"]["max"][0]:
                ty = a[3] / 2
                for m in models:
                    m.translate(0, ty, 0)            

    def intercept2d(self, x0, y0, x1, y1, y):
        """ Apply the intercept theorem in 2D """
        return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
                    
    def slice_facet(self, facet, z):
        """ Slice a facet at height z """

        # Coordinates of the resulting segment
        p = [ [None, None], [None, None] ]
        n = 0
        
        # Vertices of the facet
        v0 = [ facet[0], facet[1], facet[2] ]
        v1 = [ facet[3], facet[4], facet[5] ]
        v2 = [ facet[6], facet[7], facet[8] ]
                
        # If 2 vertices of the facet are in the slicing plan, add the edge
        if v0[2] == z and v1[2] == z:
            p[0][0], p[0][1], p[1][0], p[1][1] = v0[0], v0[1], v1[0], v1[1]
            n = 2
        elif v0[2] == z and v2[2] == z:
            p[0][0], p[0][1], p[1][0], p[1][1] = v0[0], v0[1], v2[0], v2[1]
            n = 2
        elif v1[2] == z and v2[2] == z:
            p[0][0], p[0][1], p[1][0], p[1][1] = v1[0], v1[1], v2[0], v2[1]
            n = 2
        else:
            # Compute distance between the slicing plan and each vertex
            dv0, dv1, dv2 = v0[2] - z, v1[2] - z, v2[2] - z

	    # Slicing plan intersects the triangle
	    # Check which edges of the triangle is intersecting the plan and use the interception theorem
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
                if v0[2] == z:
                    p[n][0], p[n][1] = v0[0], v0[1]
                    n += 1
                if v1[2] == z:
                    p[n][0], p[n][1] = v1[0], v1[1]
                    n += 1
                if v2[2] == z:
                    p[n][0], p[n][1] = v2[0], v2[1]
                    n += 1

        return n, p[0][0], p[0][1], p[1][0], p[1][1]

    def optimize_path(self, segs):
        """ Take a list of segments and organize it to a continuous list of points """
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
                    path.insert(0, (s[2], s[3]))
                    del segs[idx]
                    idx = -1
                elif path[0] == (s[2], s[3]):
                    path.insert(0, (s[0], s[1]))
                    del segs[idx]
                    idx = -1
                elif path[-1] == (s[0], s[1]):
                    path.append((s[2], s[3]))
                    del segs[idx]
                    idx = -1
                elif path[-1] == (s[2], s[3]):
                    path.append((s[0], s[1]))
                    del segs[idx]
                    idx = -1
                
                idx = idx + 1

            paths.append(path)

        return paths
                
    def run(self):
        """ Slicer main loop """

        verbose = self.config["verbose"]
        models = []
        
        # Load models
        for m in self.config["models"]:
            try:
                if verbose:
                    print("Loading " + m)
                    
                mdl = model.model(m, stl.mesh.Mesh.from_file(m))
                models.append(mdl)
                
            except Exception as err:
                print(str(err))
                return

        self.arrange(models)

        # Initialize slicing plan & maximal z slicing value 
        slicing_z_max = 0.0
        
        for m in models:
            m.set_slicing_plan(0.0)
            if slicing_z_max < m.bbox_max[2]:
                slicing_z_max = m.bbox_max[2]

        if verbose:
            print("Slicing height is " + str(slicing_z_max) + "mm")
            
        # Slicing loop
        layers = []
                
        for z in np.arange(0, slicing_z_max + float(self.config["quality"]), float(self.config["quality"])):
            for m in models:
                segs = []
                
                for p in m.lst_intersect:
                    facet = m.mesh.points[p]
                    (n, xa, ya, xb, yb) = self.slice_facet(facet, z)
                    
                    if n == 2:
                        segs.append((xa, ya, xb, yb))
                    else:
                        continue
                    
                if len(segs) > 0:
                    paths = self.optimize_path(segs)
                    layers.append(paths)
                
                m.update_slicing_plan(z)
                
        if verbose:
            print("Slicing done, " + str(len(layers)) + " layers extracted")

        translator = gcode.GCodeTranslator(self.config)
        
        for layer in layers:
            for path in layer:
                translator.travel(dest = path[0], speed = self.config["speed"]["travel"])

                for p in path[1:]:
                    translator.draw(p)
                    


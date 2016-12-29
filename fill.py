#!/usr/bin/env python

from util import intercept2d

class XFillLine():
    """ Filling line along X axis """
    
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        
        self.ypos = ymin
        self.pts = []
        
    def restart(self):
        self.ypos = self.ymin
        del self.pts[:]
        
    def move(self, offset):
        del self.pts[:]        
        self.ypos += offset
        return self.ypos >= self.ymin and self.ypos <= self.ymax

    def intersect(self, path, reverse = False):
        prev = path[-1]

        for p in path:
            if (self.ypos > prev[1]  and self.ypos <= p[1]) or (self.ypos > p[1] and self.ypos <= prev[1]):
                xres = intercept2d(p[0], p[1], prev[0], prev[1], self.ypos)
                yres = self.ypos
                self.pts.append((xres, yres))

            prev = p

        # Sort on X
        self.pts.sort(key = lambda p : p[0], reverse = reverse)
        
class YFillLine():
    """ Filling line along Y axis """
    
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        
        self.xpos = xmin
        self.pts = []
        
    def restart(self):
        self.xpos = self.xmin
        del self.pts[:]
        
    def move(self, offset):
        del self.pts[:]
        self.xpos += offset        
        return self.xpos >= self.xmin and self.xpos <= self.xmax

    def intersect(self, path, reverse = False):
        prev = path[-1]

        for p in path:
            if (self.xpos > prev[0] and self.xpos <= p[0]) or (self.xpos > p[0] and self.xpos <= prev[0]):
                xres = self.xpos
                # Invert X and Y coordinates
                yres = intercept2d(p[1], p[0], prev[1], prev[0], self.xpos)
                self.pts.append((xres, yres))

            prev = p

        # Sort on Y
        self.pts.sort(key = lambda p : p[1], reverse = reverse)
        
class GridPattern():

    BOTH_AXIS = -1
    X_AXIS = 0
    Y_AXIS = 1
    
    def __init__(self, xmin, ymin, xmax, ymax, step):
        
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        
        self.xfill = XFillLine(xmin, ymin, xmax, ymax)
        self.yfill = YFillLine(xmin, ymin, xmax, ymax)

        self.step = step
        self.segments = []
        
    def scan(self, paths, axis = BOTH_AXIS):        
        del self.segments[:]

        # Fill along X axis
        if axis == self.BOTH_AXIS or axis == self.X_AXIS:
            self.xfill.restart()
            zig = True
        
            while self.xfill.move(self.step) == True:
                for path in paths:
                    self.xfill.intersect(path, not zig)
                
                assert(len(self.xfill.pts) % 2 == 0)
                
                it = iter(self.xfill.pts)
                for p0, p1 in zip(it, it):
                    x0, y0 = p0[0], p0[1]
                    x1, y1 = p1[0], p1[1]
                    
                    if zig == True:
                        if x0 >= self.xmax:
                            break
                        
                        if x1 > self.xmin:
                            if x0 < self.xmin:                            
                                x0 = self.xmin
                            if x1 > self.xmax:
                                x1 = self.xmax
                    else:
                        if x0 < self.xmin:
                            break
                                    
                        if x1 < self.xmax:
                            if x0 > self.xmax:
                                x0 = self.xmax
                            if x1 < self.xmin:
                                x1 = self.xmin

                    self.segments.append((x0, y0, x1, y1))

                zig = not zig

        # Fill along Y axis
        if axis == self.BOTH_AXIS or axis == self.Y_AXIS:
            self.yfill.restart()
            zig = True
        
            while self.yfill.move(self.step) == True:
                for path in paths:
                    self.yfill.intersect(path, not zig)

                assert(len(self.yfill.pts) % 2 == 0)
            
                it = iter(self.yfill.pts)
                for p0, p1 in zip(it, it):
                    x0, y0 = p0[0], p0[1]
                    x1, y1 = p1[0], p1[1]
                
                    if zig == True:
                        if y0 >= self.ymax:
                            break

                        if y1 > self.ymin:
                            if y0 < self.ymin:
                                y0 = self.ymin
                            if y1 > self.ymax:
                                y1 = self.ymax
                    else:
                        if y0 < self.ymin:
                            break

                        if y1 < self.ymax:
                            if y0 > self.ymax:
                                y0 = self.ymax
                            if y1 < self.ymin:
                                y1 = self.ymin

                    self.segments.append((x0, y0, x1, y1))

                zig = not zig

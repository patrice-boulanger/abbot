#!/usr/bin/env python3

import numpy as np
import pylab as pl
from mpl_toolkits import mplot3d
from matplotlib import pyplot
from matplotlib import collections as mc

def show_mesh(msh):
    # Create a new plot
    figure = pyplot.figure()
    axes = mplot3d.Axes3D(figure)

    for m in msh:
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(m.vectors))
        # Auto scale to the mesh size
        scale = m.points.flatten(-1)
        axes.auto_scale_xyz(scale, scale, scale)

    # Show the plot to the screen
    pyplot.show()

def show_segments(segs):
    c = np.array([(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
    lc = mc.LineCollection(segs, colors=c, linewidths=2)
    fig, ax = pl.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    pyplot.show()

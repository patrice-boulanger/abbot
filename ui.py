#!/usr/bin/env python3

from mpl_toolkits import mplot3d
from matplotlib import pyplot

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

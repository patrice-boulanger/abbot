#!/usr/bin/env python3

import os, sys, getopt, json

# Our stuffs
from slicer import Slicer
from model import Model
from optimizer import Optimizer
from gcode import GCode

def usage():
    """ Print an help message """    
    print("usage: abbot.py [OPTIONS]")
    print("options:")
    print(" -c file,  --config=file   loads configuration from 'file'")
    print(" -h,       --help          print this help message")
    print(" -m file,  --model=file    loads model from 'file'")
    print(" -o file,  --output=file   write the output to 'file'")
    print(" -v,       --verbose       be verbose")

def init_configuration(config):
    # Basic default configuration
    # Distance are expressed in mm and speeds in mm/s

    config["verbose"] = False
    config["output"] = None

    # Printer
    config["printer"] = dict()
    config["printer"]["gcode"] = "marlin"
    config["printer"]["min"] = [ 0, 0, 0 ]
    config["printer"]["max"] = [ 200, 200, 200 ]
    
    # Extruder(s)
    config["extruder"] = dict()        
    config["extruder"]["nozzle_diameter"] = 0.35
    config["extruder"]["filament_diameter"] = 1.75 
    config["extruder"]["temperature"] = 200
    config["extruder"]["offset_x"] = 0
    config["extruder"]["offset_y"] = 0
    config["extruder"]["fan_speed"] = 255
    config["extruder"]["retract"] = dict()
    config["extruder"]["retract"]["speed"] = 110
    config["extruder"]["retract"]["distance"] = 4
    
    # Layer height
    config["quality"] = 0.2
    
    # Speeds
    config["speed"] = dict()
    config["speed"]["print"] = 40
    config["speed"]["travel"] = 150
    config["speed"]["first_layer"] = 30
    config["speed"]["outer_perimeter"] = 30
    config["speed"]["inner_perimeter"] = 40
    config["speed"]["infill"] = 60
    config["speed"]["skin_infill"] = 30
    
    # Infill
    config["thickness"] = dict()
    config["thickness"]["shell"] = 0.7
    config["thickness"]["top_bottom"] = 0.6
        
def main(argv):
    """ Program entry point """

    config = dict()
    init_configuration(config)
    config_loaded = False
    
    filenames = []
    models = []

    output = None
    verbose = False
    
    try:
        opts, args = getopt.getopt(argv, "c:hm:o:s:v", [ "config", "help", "model", "output", "set", "verbose" ])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)

    for o, a in opts:
        if o == '-c':
            try:
                with open(a, "r") as f:
                    config = json.load(f)
                    config_loaded = True
            except Exception as err:
                print(str(err))
                sys.exit(1)                
        elif o == '-h':
            usage()
            sys.exit(0)
        elif o == '-m':
            filenames.append(a)
        elif o == '-o':
            output = a
        elif o == '-v':
            verbose = True
        else:
            print("invalid option " + o)
            usage()
            sys.exit(1)

    # If no configuration has been specified, try to load default file 
    if not config_loaded and os.path.isfile("./abbot.json"):
        try:
            with open("./abbot.json", "r") as f:
                config = json.load(f)
        except Exception as err:
            print(str(err))
            sys.exit(1)                

    if output != None:
        config["output"] = output

    config["verbose"] = verbose
            
    if len(filenames) == 0:
        print("no filenames specified")
        usage()
        sys.exit(1)
    else:
        for f in filenames:
            try:
                models.append(Model(f))
            except Exception as err:
                print("Loading " + f + ": " + str(err))
                return
                 
    config["filenames"] = filenames

    # Let's go
    slicer = Slicer(config, models)
    slices = slicer.build_slicing_plan()

    optimiser = Optimizer(config)
    layers = optimiser.optimize(slices)

    gcode = GCode(config)
    gcode.dump(layers)
    
if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)

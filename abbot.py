#!/usr/bin/env python3

import sys, getopt
import json

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
    print(" -s k=v,   --set=k=v       set the value of the key 'k' to value 'v'")
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
    
    filenames = []
    models = []
    
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
            except Exception as err:
                print(str(err))
                sys.exit(1)                
        elif o == '-h':
            usage()
            sys.exit(0)
        elif o == '-m':
            filenames.append(a)
        elif o == '-o':
            config["output"] = a
        elif o == '-v':
            config["verbose"] = True
        else:
            print("invalid option " + o)
            usage()
            sys.exit(1)

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

    slcr = Slicer(config, models)
    layers = slcr.run()

    optm = Optimizer(config)
    plan = optm.optimize(layers)

    gcode = GCode(config)
    gcode.dump(plan)
    
if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)

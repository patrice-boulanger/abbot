#!/usr/bin/env python3

import sys, getopt
import json

from slicer import slicer

def usage():
    """ Print an help message """    
    print("usage: abbot.py [OPTIONS]")
    print("options:")
    print(" -c file,  --config=file   loads configuration from 'file'")
    print(" -h,       --help          print this help message")
    print(" -m file,  --model=file    loads model from 'file'")
    print(" -o file,  --output=file   write the output to 'file'") 
    print(" -v,       --verbose       be verbose")
    
def main(argv):
    """ Program entry point """

    app = slicer.slicer()

    try:
        opts, args = getopt.getopt(argv, "c:hm:o:v", [ "config", "help", "model", "output", "verbose" ])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)

    output = None
    verbose = False
    models = []
    
    for o, a in opts:
        if o == '-c':
            try:
                with open(a, "r") as f:
                    cfg = json.load(f)
                    app.config = cfg
            except Exception as err:
                print(str(err))
                sys.exit(1)                
        elif o == '-h':
            usage()
            sys.exit(0)
        elif o == '-m':
            models.append(a)
        elif o == '-o':
            output = a
        elif o == '-v':
            verbose = True
        else:
            print("invalid option " + o)
            usage()
            sys.exit(1)

    if len(models) == 0:
        print("no models specified")
        usage()
        sys.exit(1)
            
    if output != None:
        app.config["output"] = output

    app.config["verbose"] = verbose
    app.config["models"] = models
    
    app.run()
    
if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)

    

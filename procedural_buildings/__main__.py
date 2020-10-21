import sys, getopt
from .Processor import Processor
from os import getcwd
from .Scope import Scope
import numpy as np

DEFAULT_SEP = 10
DEFAULT_SCOPE_SIZE = [10,10,10]

def main(argv):
    inFile = ""
    outFile = ""
    rev = False
    n = 1
    sep = DEFAULT_SEP
    filePerObj = False
    startRule = 'plot'
    startScope = Scope.freshScope(np.array([0,0,0]),np.array(DEFAULT_SCOPE_SIZE))
    usage = 'Usage:\nprocedural_buildings -i <input_file> -o <output_file> [-s | --start_scope <x_min,y_min,z_min,x_max,y_max,z_max>] [-R | --start_rule <start_rule>] [-r | --reverse] [-n <num_buildings>] [-d | --separation <separation_distance>] [-f | --file_per_obj]'
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:R:rn:d:f",["ifile=","ofile=","start_scope=","start_rule=","reverse","separation=","file_per_obj"])
    except getopt.GetoptError:
        print("Option error")
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inFile = arg
        elif opt in ("-o", "--ofile"):
            outFile = arg
        elif opt in ("-s", "--start_scope"):
            try:
                coords = [int(coord) for coord in arg.split(",")]
                assert(len(coords) == 6)
                startScope = Scope.freshScope(np.array(coords[:3]),np.array(coords[3:]))
            except:
                print("Invalid scope argument.")
                print(usage)
                sys.exit()
        elif opt in ("-R", "--start_rule"):
            startRule = arg
        elif opt in ("-r", "--reverse"):
            rev = True
        elif opt == "-n":
            n = int(arg)
        elif opt in ("-d", "--separation"):
            sep = int(arg)
        elif opt in ("-f", "--file_per_obj"):
            filePerObj = True
   
    if not inFile or not outFile:
        print("Please provide both an input and output file")
        print(usage)
        sys.exit()
    p = Processor()
    p.grammarDir = getcwd() + "\\"
    p.outputDir = p.grammarDir
    p.engineeredDir = p.grammarDir
    if rev:
        # Check if provided an object file or a file with list of filenames
        if inFile.split(".")[-1] == "obj":
            objFiles = [inFile]
        else:
            with open(inFile) as f:
                objFiles = f.read().splitlines()
        p.objsToGrammar(objFiles, outFile)
        
    else:
        if filePerObj:
            p.grammarToManyObjFiles(inFile, startRule, startScope, n, outFile)
        else:
            p.grammarToManyObjs(inFile, startRule, startScope, n, sep, outFile)

if __name__ == "__main__":
    main(sys.argv[1:])



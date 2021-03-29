#! /usr/bin/python3

import os,sys

def main(fvFile):
    print('bbb', fvFile)

if __name__ == '__main__':
    print('aaa', sys.argv)
    print(len(sys.argv))

    if len(sys.argv) < 2:
        print(" Usage: {} <featurevector.fv>".format(sys.argv[0]))
        sys.exit(1)
    
    main(sys.argv[1])
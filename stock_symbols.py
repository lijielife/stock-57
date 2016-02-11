#!/usr/bin/env python

import os
import argparse as ap

def get_cmd_line():
    parser = ap.ArgumentParser(description='update stock symbols')
    parser.add_argument("data_dir")
    cmd_args = parser.parse_args()
    data_dir = os.path.abspath(cmd_args.data_dir)
    if not os.path.exists(data_dir):
        print "%s does not exist!" % data_dir
        os.sys.exit()

    return data_dir

def main():
    data_dir = get_cmd_line()
    
if __name__ == "__main__":
    main()


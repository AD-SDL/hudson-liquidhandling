import argparse
import json
import zmq
import time
import os
import sys
import datetime

def simple_test(plate_id): 
    print(plate_id)
    print("Simple test worked")

def main(args):
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-id", "--plate_id", help="ID of the plate associated with data being sent", required=False, type=int
    )
    args = vars(parser.parse_args())
    # print(
    #     "time = {}, dir = {}, ext = {}".format(args["time"], args["dir"], args["ext"])
    # )

    simple_test(args["plate_id"])


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
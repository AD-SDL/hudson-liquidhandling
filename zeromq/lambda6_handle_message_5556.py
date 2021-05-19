""" Lambda6 message handler 
- write message received to log
- determine if message is formatted correctly
- write contents of message to approptiate numer of files on lambda 6
- call QC module on data files 
"""

import os
import sys
import json
from path import Path
from utils.build_dataframe import build_dataframe


def lambda6_handle_message(decoded_message):

    lambda6_data_path = "/lambda_stor/data/hudson/data/"

    # * extract message address and body
    json_decoded = json.loads(decoded_message)

    return_val = "PASS"
    print(f"Handling message: {json_decoded}")

    print(json_decoded)
    for k in json_decoded:
        file_data = json_decoded[k]
        filename = file_data["path"]
        print(f"filename {filename[0]}")
        df = build_dataframe(filename)
        print(f"data frame basename {df}")

    print(f"Done handling message: {json_decoded}")
    return return_val


def main(args):
    decoded_message = sys.argv[1]
    lambda6_handle_message(decoded_message)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

import os
import os.path
from datetime import datetime
import time
from stat import *
import pathlib
import json

def generateFileManifest(filename, manifest_filename=None):

    string = ""
    data = {}
    if os.path.isfile(filename):
        f = pathlib.Path(filename)

        data[os.path.abspath(filename)] = {
                    'ctime': [str(f.stat().st_ctime), str(datetime.fromtimestamp(f.stat().st_ctime))],
                    'mtime':[str(f.stat().st_mtime), str(datetime.fromtimestamp(f.stat().st_mtime))]
                    }

        json_data = json.dumps(data)

        if manifest_filename != None:
            with open(manifest_filename, "w+") as manifest_file:
                manifest_file.write(json_data)

    else:
        print ("skipping bad filename: {}".format(filename))

    return data

import os
import time
from datetime import datetime
from stat import *
import pathlib


def checkDir(dir, last_mtime=0):
    """
    :param str dir: The directory to check
    :param int last_mtime: Time in seconds since previous check

    mtime - look back the previous mtime seconds for files that
    have changed.

    This needs to be validated for case when mtime is very close
    to ctime - last_mtime
    """

    ctime = time.time()
    ptime = ctime - last_mtime

    file_list = [f for f in os.listdir(dir) if not f.startswith(".")]
    file_list = [f for f in file_list if not os.path.isdir(f)]
    # save the absolute path instead of just filename
    file_list = [
        os.path.join(os.path.abspath(dir), f)
        for f in os.listdir(dir)
        if not f.startswith(".")
    ]
    # file_list = [f for f in os.listdir(dir) if not f.startswith('.')]
    # print("files newer than {}".format(datetime.fromtimestamp(ptime)))

    new_files = []
    for f in file_list:
        print(f)
        obj = pathlib.Path(f)
        if obj.stat().st_mtime >= ptime:
            # print ("{} {}".format(
            #    datetime.fromtimestamp(obj.stat().st_mtime), f ))
            new_files.append(os.path.abspath(f))

    return new_files

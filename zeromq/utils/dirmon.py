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

    _file_list = [f for f in os.listdir(dir) if not f.startswith(".")]
    file_list = [f for f in _file_list if not os.path.isdir(f)]
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
        obj = pathlib.Path(f)
        print(obj.stat().st_mtime)
        print(ptime)
        if obj.stat().st_mtime >= ptime:
            # print ("{} {}".format(
            #    datetime.fromtimestamp(obj.stat().st_mtime), f ))
            new_files.append(os.path.abspath(f))
    return new_files


def find_most_recent(dir_path, extension=""):  
    """
    returns most recent file (by mtime) in given directory with a certain extension

    :param str dir_path: The directory to check
    :param str extension: (optional, The file extension to look for)

    output: path of newest file in directory (str)

    usage examples: find_most_recent("C://labautomation//data", ".xlsx")
                    find_most_recent("C://labautomation//data")
    """

    newest_file_path = ""
    newest_mtime = None
    try:
        for filename in os.listdir(dir_path):
            if not filename.endswith(extension): # check for correct extension
                continue
            elif filename.startswith("~"): # ignore hidden files
                continue
            else: 
                file_path = os.path.join(dir_path, filename)
                obj = pathlib.Path(file_path)
                mtime = obj.stat().st_mtime
                if newest_mtime == None: # set variables in first loop
                    newest_file_path = file_path
                    newest_mtime = mtime
                if mtime > newest_mtime: # keep track of newest file
                    newest_file_path = file_path
                    newest_mtime = mtime
        return newest_file_path
    except OSError as e: 
        print(e)



""" Module of qc methods """
import sys
import os
from pathlib import Path

sys.path.append("../utils/")
sys.path.append("../../")
sys.path.append("../../rdbms/")


import csv
import pandas as pd
from utils.data_utils import parse_hidex


def build_dataframe(filenames, basename=None):
    """Builds a dataframe using one or more Hidex files..

    Params:
        filenames - A 1-dimensional array file names

    Returns:
        string - basename of data frame files (data, rows, cols)

    Description:
        The basic idea is that this method takes as input list
        of filenames that has hidex data.

        Writes out data, cols, rows, labels files using
    """

    # define data frame file name
    if basename == None:
        return_val = "basename"
    else:
        return_val = basename

    # set up rows, cols and data variables
    cols = ["Blank-corrected OD(590) Kinetic cycle #1"]
    rows = pd.DataFrame()
    data = pd.DataFrame()

    # loop over the set if filenames appending to samples and data
    for f in filenames:
        print("parsing {}".format(f))
        df = parse_hidex(f)
        print(df)
        data = data.append(df.iloc[:, -1:])
        rows = rows.append(df[["Well"]], ignore_index=True)

    # save the files and return the file basename
    print(f"writing files to {return_val}")
    data.to_csv(return_val + "_data.csv", sep=",", header=None, index=None)
    rows.to_csv(return_val + "_rows.csv", sep=",", header=None, index=None)
    pd.DataFrame(cols).to_csv(
        return_val + "_cols.csv", sep=",", header=None, index=None
    )

    return return_val


def main(args):
    filename = args[0]
    basename = os.path.basename(filename)
    basename = str(Path(basename).with_suffix(""))
    df = build_dataframe([filename, filename], basename=basename)
    print(df)


if __name__ == "__main__":
    # execute only if run as a script
    main([(sys.argv[1])])

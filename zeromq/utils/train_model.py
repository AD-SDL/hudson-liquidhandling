import sys
import os

sys.path.append("../utils/")
sys.path.append("./utils/")
sys.path.append("../rdbms/")
sys.path.append("../../rdbms/")
sys.path.append("../../../rdbms")

from connect import connect

# connect to mysql, cnx is global to this file
cnx = connect()


def train_model(filenames, basename=None):
    """trains a model
    params: list of data frame file names
    return: list of model file names
    """

    print(f"\ntraining model on {filenames}")

    # stub - implement this when we have a model to train

    if basename == None:
        basename = "basename"

    with open(basename + "_model.h5", "w") as f:
        f.write("PASS")
    new_files = [basename + "_model.h5"]
    # end stub implementation

    return new_files


def main(args):
    filename = args[0]
    train_model([filename])
    return "done training"


if __name__ == "__main__":
    # execute only if run as a script
    main([(sys.argv[1])])

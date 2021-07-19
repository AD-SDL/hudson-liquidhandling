import sys

sys.path.append("../utils/")
sys.path.append("./utils/")
sys.path.append("../rdbms/")
sys.path.append("../../rdbms/")
sys.path.append("../../../rdbms")

from connect import connect

# connect to mysql, cnx is global to this file
cnx = connect()


def run_inferencing(filenames, basename=None):
    """run model in inferencing mode (predict)
    params: model file name and sample dataframe
    return: a file of predictions
    """

    print(f"RUN INFERENCING BASENAME: {basename}")
    print(f"\ninferring using filenames: {filenames}")

    # stub - implement this when we have a model to train
    if basename == None:
        basename = "basename"

    with open(basename + "_predictions.csv", "w") as f:
        f.write("PASS")
    new_files = [basename + "_predictions.csv"]
    # end stub implementation

    return new_files


def main(filenames):
    run_inferencing(filenames)
    return "done predicting"


if __name__ == "__main__":
    # execute only if run as a script
    main([(sys.argv[1])])

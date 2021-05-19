""" Module of qc methods """
import sys

sys.path.append("../utils/")
sys.path.append("./utils/")
sys.path.append("../../../rdbms")

from data_utils import parse_hidex
import csv
import pandas as pd


sys.path.append("../rdbms/")
sys.path.append("../../rdbms/")
from connect import connect


# connect to mysql, cnx is global to this file
cnx = connect()


def run_qc(values):
    """Runs qc on data from the lab.

    Params:
        values - A 1-dimensional array of values

    Returns:
        boolean - based on if qc rules passed

    Description:
        The basic idea is that this method takes as input a file
        name that has hidex data.

        A list of values associated with the blanks in the file
        is constructed and z-scores are computed against all blanks
        in the database.

        If any z_score is greater than 1.5, then the plate fails.
    """

    return_val = "PASS"

    z_scores = z_score(values)
    for z in z_scores:
        if z >= 1.5:
            print("FAIL sample has z_xcore {} >= 1.5".format(z))
            return_val = "FAIL"

    print(f"done running qc on {input}")
    return return_val


def z_score(values):
    sql = (
        "select avg(value) avg, std(value) std from plate p, assay_plate ap "
        "where p.plate_id=ap.plate_id and ap.type='hidex' "
        "and p.type='assay' and ap.sample='blank' group by ap.sample"
    )
    cursor = cnx.cursor()
    cursor.execute(sql)
    (avg, std) = cursor.fetchone()
    print("avg {} std {}".format(avg, std))

    z_scores = []
    for val in values:
        z_scores.append((val - avg) / std)
    print("z-scores: {}".format(z_scores))

    return z_scores


def main(args):
    filename = args[0]
    df = data_utils.parse_hidex(filename)
    values = df.loc[df["Sample"] == "Blank"].to_numpy()[:, 3].astype(float)
    result = run_qc(values)
    print("result: {}".format(result))


if __name__ == "__main__":
    # execute only if run as a script
    main([(sys.argv[1])])

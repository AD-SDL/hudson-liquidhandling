""" Module of qc methods """
import sys

sys.path.append("../../")
sys.path.append("../../rdbms/")

from rdbms.connect import connect
from rdbms import config

import csv
import pandas as pd

# cnx is global to this file
cnx = connect()


def parse(filename):
    """parses the Hidex csv file

    Params:
        filename: the complete path and name of the Hidex cvs file

    Returns:
        df: a pandas data frame

    Description:


    """
    df = pd.DataFrame()

    DATA = False
    with open(filename, newline="") as csvfile:
        csv.QUOTE_NONNUMERIC = True
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 0 and row[0] == "Well":
                df = pd.DataFrame(columns=row)
                DATA = True
                continue
            if DATA == True:
                df.loc[len(df.index) + 1] = row

    return df


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
    df = parse(filename)
    values = df.loc[df["Sample"] == "Blank"].to_numpy()[:, 3].astype(float)
    result = run_qc(values)
    print("result: {}".format(result))


if __name__ == "__main__":
    # execute only if run as a script
    main([(sys.argv[1])])

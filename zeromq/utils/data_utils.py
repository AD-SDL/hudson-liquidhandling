import sys
import csv
import pandas as pd

def parse_hidex(filename):
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


def test(filename):
    df = parse_hidex(filename)
    print(df)
    return df

if __name__ == "__main__":
    test(sys.argv[1])

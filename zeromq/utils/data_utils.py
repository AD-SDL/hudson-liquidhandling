import sys
import csv
import pandas as pd
import openpyxl
import os


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
        print(f"opened {filename}")
        csv.QUOTE_NONNUMERIC = True
        reader = csv.reader(csvfile)
        for row in reader:
            row = [x.strip() for x in row]
            if len(row) > 0 and row[0] == "Plate #":
                df = pd.DataFrame(columns=row)
                DATA = True
                continue
            if DATA == True:
                df.loc[len(df.index) + 1] = row

    return df


def excel_to_csv(filename):
    """
    Extracts Raw OD(590) data from Hidex excel file into csv file

    :param str filename: filename of Hidex excel file to convert

    output: path of new csv file (str)

    """
    csv_filename = None

    if os.path.exists(filename):
        excel_basename = os.path.splitext(os.path.basename(filename))[0]
        csv_filename = excel_basename + "_RawOD.csv"
        csv_filepath = filename.replace(os.path.basename(filename), csv_filename)

    # convert Raw OD(590) excel sheet to new csv file
    excel_OD_data = pd.read_excel(filename, sheet_name="Raw OD(590)", index_col=None)
    excel_OD_data.to_csv(csv_filepath, encoding="utf-8", index=False)

    return csv_filepath


def test(filename):
    df = parse_hidex(filename)
    print(df)
    return df


if __name__ == "__main__":
    test(sys.argv[1])

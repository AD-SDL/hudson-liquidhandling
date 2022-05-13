import argparse

from .post_transformation import generate_post_transformation


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--is_test", help="use -t or --is_test only if the run is a test and the data can be deleted", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":

    args = parse_args()

    generate_post_transformation(args["is_test"])

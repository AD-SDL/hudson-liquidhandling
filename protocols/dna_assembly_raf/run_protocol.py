


from . import step1
from . import step2


full_protocol = [
    step1,
    step2,
    ]




if __name__ == "__main__":
    # handle command line args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", 
        "--is_test",
        help="use -t or --is_test only if the run is a test and the data can be deleted",  
        action="store_true",
    )
    args = vars(parser.parse_args())

    # pass to method
    generate_post_transformation(args["is_test"])

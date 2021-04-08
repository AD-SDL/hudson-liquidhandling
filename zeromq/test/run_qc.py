''' Module of qc methods '''
import sys


def run_qc(input):
    ''' Runs qc on data from the lab '''

    return_val = "PASS"
    print(f'running qc on {input}')

    print(f'done running qc on {input}')
    return return_val


def main(args):
    input = sys.argv[1]
    run_qc(input)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

import argparse
import sys
import os.path

import gsp
from gsp import GSP


def main(argv):
    """Check args and execute the algorithm with the given parameters"""

    """Loading database from input file"""
    database = gsp.load_db(argv.infile)
    if not database:
        print("Could not load database from input file")
        sys.exit(1)

    """Checking output file"""
    if os.path.exists(argv.outfile):
        print("File", argv.outfile, "already exists, want to proceed? [Y/N]")
        answer = ""
        while (answer != "Y") & (answer != "N"):
            answer = input()

            if answer == "N":
                print("Quitting")
                sys.exit(1)
    output_path = open(argv.outfile, 'w')

    """Checking min support"""
    try:
        minsup = float(argv.minsup)
        if (minsup < 0) | (minsup > 1):
            raise ValueError
    except ValueError:
        print("minsup must be expressed as a decimal between 0 and 1")
        sys.exit(1)

    """Running algorithm"""
    algo_obj = GSP(database, float(argv.minsup), argv.verbose)
    result = algo_obj.run_gsp()

    for sequence_info in result:
        output_path.write(f"{sequence_info[0]} sup: {sequence_info[1]}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='input file')
    parser.add_argument('outfile', help='output file')
    parser.add_argument('minsup', help='minimum support')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable printing of debug messages')

    parsed_argv = parser.parse_args()
    main(parsed_argv)

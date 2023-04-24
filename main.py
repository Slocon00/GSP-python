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
        sys.exit(1)

    """Checking output file"""
    if os.path.exists(argv.outfile):
        print("File", argv.outfile, "already exists, want to proceed? [Y/N]")
        answer = ""
        while (answer != "Y") & (answer != "N"):
            answer = input()

            if answer == "N":
                sys.exit(1)
    output_path = open(argv.outfile, 'w')

    """Checking min support"""
    # todo minsup check

    """Running algorithm"""
    algo_obj = GSP(database, float(argv.minsup), argv.verbose)
    result = algo_obj.run_gsp()

    # todo print to outfile
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='input file')
    parser.add_argument('outfile', help='output file')
    parser.add_argument('minsup', help='minimum support')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable printing of debug messages')

    parsed_argv = parser.parse_args()
    main(parsed_argv)

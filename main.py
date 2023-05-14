import argparse
import math
import sys
import os.path
import gsp
from gsp import GSP
from database_gen import DatabaseGenerator
import logging
logging.basicConfig(level=logging.NOTSET, stream=sys.stdout,
                    format="%(levelname)s:%(module)s:%(message)s", force=True)


def setup_subparsers(parser):
    """Add subparsers for each algorithm"""
    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'subcommand'

    """Subparser for GSP"""
    parser_gsp = \
        subparsers.add_parser('GSP', help='Generalized Sequential Pattern algorithm')
    parser_gsp.add_argument('infile', help='input file')
    parser_gsp.add_argument('outfile', help='output file')
    parser_gsp.add_argument('minsup', type=float, help='minimum support')
    parser_gsp.add_argument('-t', type=int, nargs=3, default=[math.inf, 1, math.inf],
                            metavar=('maxgap', 'mingap', 'maxspan'), help='specify time constraints')

    parser_gsp.add_argument('-v', '--verbose', action='store_true', default=False,
                            help='enable printing of debug messages')

    """Subparser for sequence database generator"""
    parser_dbgen = \
        subparsers.add_parser('DatabaseGen', help='sequence database generator')
    parser_dbgen.add_argument('outfile', help='output file')
    parser_dbgen.add_argument('size', type=int, help='# of sequences')
    parser_dbgen.add_argument('nevents', type=int, help='# of unique events')
    parser_dbgen.add_argument('maxevents', type=int, help='max # of events in an element')
    parser_dbgen.add_argument('maxelems', type=int, help='max # of elements in a sequence')
    parser_dbgen.add_argument('-s', '--seed', default=None, help='seed for random event generation')
    parser_dbgen.add_argument('-v', '--verbose', action='store_true', default=False,
                              help='enable printing of debug messages')


def main(argv):
    """Check args and execute the algorithm with the given parameters"""
    parser = argparse.ArgumentParser()
    setup_subparsers(parser)
    parsed_argv = parser.parse_args()

    if parsed_argv.subcommand == "GSP":
        """Loading database from input file"""
        database = gsp.load_db(parsed_argv.infile)
        if not database:
            print("Could not load database from input file")
            sys.exit(1)

        """Checking output file"""
        if os.path.exists(parsed_argv.outfile):
            print("File", parsed_argv.outfile, "already exists, want to proceed? [Y/N]")
            answer = ""
            while answer not in ["Y", "y", "N", "n"]:
                answer = input()

                if answer in ["N", "n"]:
                    print("Quitting")
                    sys.exit()
        output_path = open(parsed_argv.outfile, 'w')

        """Checking min support"""
        if (parsed_argv.minsup < 0) | (parsed_argv.minsup > 1):
            print("minsup must be a decimal between 0 and 1")
            sys.exit(1)

        """Running GSP algorithm"""
        algo_obj = GSP(database, parsed_argv.minsup, parsed_argv.t[0],
                       parsed_argv.t[1], parsed_argv.t[2], parsed_argv.verbose)
        result = algo_obj.run_gsp()

        """Printing to output file"""
        for sequence_info in result:
            for element in sequence_info[0]:
                for event in element:
                    output_path.write(f"{event} ")
                output_path.write("-1 ")
            output_path.write(f"#SUP: {sequence_info[1]}\n")

    elif parsed_argv.subcommand == "DatabaseGen":
        """Checking output file"""
        if os.path.exists(parsed_argv.outfile):
            print("File", parsed_argv.outfile, "already exists, want to proceed? [Y/N]")
            answer = ""
            while answer not in ["Y", "y", "N", "n"]:
                answer = input()

                if answer in ["N", "n"]:
                    print("Quitting")
                    sys.exit()
        output_path = open(parsed_argv.outfile, 'w')

        """Generating database"""
        algo_obj = DatabaseGenerator(parsed_argv.size, parsed_argv.nevents,
                                     parsed_argv.maxevents, parsed_argv.maxelems,
                                     parsed_argv.seed, parsed_argv.verbose)
        result = algo_obj.generate_sequence_database()

        """Printing to output file"""
        for sequence in result:
            for element in sequence:
                for event in element:
                    output_path.write(f"{event} ")
                output_path.write("-1 ")
            output_path.write("-2\n")


if __name__ == "__main__":
    main(sys.argv)

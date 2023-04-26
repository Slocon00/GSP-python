import random
import sys
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="%(levelname)s:%(message)s")


class DatabaseGenerator:
    """A class that represents a sequence database generator.

    An instance of the DatabaseGenerator class can generate a sequence database
    with a specific set of parameters.
    """

    def __init__(self, size, nevents, maxevents, maxelems, seed=None, verbose=False):
        """Initialize an instance with the given requirements:
            size: overall number of sequences in the database
            nevents:    number of unique events in the database
            maxevents:  max number of events contained in a single element
            maxelems:   max number of elements contained in a single sequence
            seed:       the seed to be used for random number generation (if not
                        provided, random's default choice of seed is used)
        """
        self.output = []

        self.size = size
        self.nevents = nevents
        self.maxevents = maxevents
        self.maxelems = maxelems

        if seed is not None:
            random.seed(seed)

        if not verbose:
            logging.disable()

    def generate_sequence_database(self):
        """Generate a simple sequence database"""
        for i in range(self.size):
            sequence = []
            for j in range(1, random.randint(1, self.maxelems) + 1):
                """Element must not contain duplicate events, events are sorted
                in ascending order
                """
                element = set()
                for k in range(1, random.randint(1, self.maxevents) + 1):
                    element.add(random.randint(1, self.nevents))

                logging.info(f"Element: {element}")
                sequence.append(list(element))

            logging.info(f"Sequence: {sequence}")
            self.output.append(sequence)

        return self.output

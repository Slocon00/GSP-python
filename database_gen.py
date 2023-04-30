import random
import math
import logging
logger = logging.getLogger(__name__)


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

        """mu and sigma values for normal distribution"""
        self.mu_size = self.maxelems*3/4
        self.mu_elem = self.maxevents*3/4
        self.mu_event = self.maxevents*3/4
        self.s_size = 1.5
        self.s_elem = 1.5
        self.s_event = 2

        if seed is not None:
            random.seed(seed)

        if not verbose:
            logger.disabled = True

    def generate_sequence_database(self):
        """Generate a simple sequence database"""
        for i in range(self.size):
            sequence = []

            """Generate a random length for the sequence"""
            seq_length = 0
            while (seq_length < 1) | (seq_length > self.maxelems):
                seq_length = math.floor(random.normalvariate(self.mu_size, self.s_size) + 0.5)
                logger.info(f"random seq_length: {seq_length}")

            for j in range(seq_length):
                """Element must not contain duplicate events, events are sorted
                in ascending order
                """
                element = set()

                """Generate a random length for the element"""
                elem_length = 0
                while (elem_length < 1) | (elem_length > self.maxevents):
                    elem_length = math.floor(random.normalvariate(self.mu_elem, self.s_elem) + 0.5)
                    logger.info(f"random elem_length: {elem_length}")

                while len(element) < elem_length:
                    event = -1
                    while (event < 1) | (event > self.nevents):
                        event = math.floor(random.normalvariate(self.mu_event, self.s_event) + 0.5)
                    element.add(event)

                logger.info(f"Element: {element}")
                sequence.append(list(element))

            logger.info(f"Sequence: {sequence}")
            self.output.append(sequence)

        return self.output

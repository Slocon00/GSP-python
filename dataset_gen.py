import random
import math
import logging
logger = logging.getLogger(__name__)


class DatasetGenerator:
    """A class that represents a sequence dataset generator.

    An instance of the DatasetGenerator class can generate a sequence dataset
    with a specific set of parameters.
    """

    def __init__(self, size, nevents, maxevents, avgelems, seed=None, verbose=False):
        """Initialize an instance with the given requirements:
            size: overall number of sequences in the dataset
            nevents:    number of unique events in the dataset
            maxevents:  max number of events contained in a single element
            avgelems:   average number of elements contained in a single sequence
            seed:       the seed to be used for random number generation (if not
                        provided, random's default choice of seed is used)
        """

        self.size = size
        self.nevents = nevents
        self.verbose = verbose

        if maxevents > nevents:
            self.maxevents = nevents
        else:
            self.maxevents = maxevents
        self.avgelems = avgelems

        """mu and sigma values for normal distribution"""
        self.mu_length = self.avgelems
        self.mu_elem = self.maxevents * 3 / 4
        self.mu_event = self.nevents * 3 / 4
        self.s_length = 2
        self.s_elem = self.maxevents * 3 / 4
        self.s_event = self.nevents * 3 / 4

        if seed is not None:
            random.seed(seed)

        if not verbose:
            logger.disabled = True

    def generate_sequence_dataset(self):
        """Generate a sequence dataset"""
        output = []
        for i in range(self.size):
            sequence = []

            """Generate a random length for the sequence"""
            seq_length = 0
            while seq_length < 1:
                seq_length = math.floor(random.gauss(self.mu_length, self.s_length) + 0.5)

                if self.verbose:
                    logger.info(f"random seq_length: {seq_length}")

            for j in range(seq_length):
                """Element must not contain duplicate events, events are sorted
                in ascending order
                """
                element = set()

                """Generate a random length for the element"""
                elem_length = 0
                while (elem_length < 1) | (elem_length > self.maxevents):
                    elem_length = math.floor(random.gauss(self.mu_elem, self.s_elem) + 0.5)

                    if self.verbose:
                        logger.info(f"random elem_length: {elem_length}")

                while len(element) < elem_length:
                    event = -1
                    while (event < 1) | (event > self.nevents):
                        event = math.floor(random.gauss(self.mu_event, self.s_event) + 0.5)
                    element.add(event)

                if self.verbose:
                    logger.info(f"Element: {element}")

                sorted_element = list(element)
                sorted_element.sort()
                sequence.append(sorted_element)

            if self.verbose:
                logger.info(f"Sequence: {sequence}")

            output.append(sequence)

        return output

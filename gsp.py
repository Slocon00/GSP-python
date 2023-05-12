from copy import deepcopy
import logging

"""Logger for tracking execution on stdout"""
logger = logging.getLogger(__name__)


class GSP:
    """A class that implements the Generalized Sequential Pattern algorithm.

    An instance of the GSP class runs the GSP algorithm on a sequence database,
    mining all frequent sequences in the database whose support is higher or
    equal than a minimum threshold.
    """

    def __init__(self, db, minsup, verbose=False):
        """Initialize an instance of the class with a reference to the database
        from which frequent sequences must be mined and a minsupport threshold
        """
        self.db = db
        self.minsup = minsup
        self.frequent_sequences = {}
        self.candidate_sequences = []
        self.output = []

        self.verbose = verbose
        if not verbose:
            logger.disabled = True

        """Find all unique events (1-sequences)"""
        for index, sequence in enumerate(self.db):
            for element in sequence:
                for event in element:
                    if event not in self.frequent_sequences:
                        self.frequent_sequences[event] = [Sequence([[event]], set())]
                    self.frequent_sequences[event][0].set_of_indexes.add(index)

    def run_gsp(self):
        """Run GSP algorithm"""
        if self.verbose:
            logger.info("STARTING GSP ALGORITHM\n")
            logger.info("*** Finding all frequent 1-sequences ***")

        """Find all frequent 1-sequences"""
        n = len(self.db)
        for event in list(self.frequent_sequences):
            support_count = len(self.frequent_sequences[event][0].set_of_indexes)
            support = support_count / n
            if support < self.minsup:
                del self.frequent_sequences[event]
            else:
                if self.verbose:
                    logger.info(f"Event: {event} - Support count: {support_count}")

        k = 2
        """Loop until there are no more frequent k-sequences"""
        while self.frequent_sequences:
            """All frequent k-1-sequences get printed to the output file"""
            self.print_frequent_sequences()

            """Generate and prune all candidate k-sequences"""
            self.generate_candidates(k)

            if k > 2:
                self.prune_candidates()

            """All frequent k-1-sequences are discarded as they're not needed"""
            for event in self.frequent_sequences:
                self.frequent_sequences[event].clear()

            """Calculate support count and find frequence k-sequences"""
            self.support_count()

            """Clear candidate sequences for next iteration"""
            self.candidate_sequences.clear()
            k += 1

        return self.output

    def generate_candidates(self, k):
        """Generate all candidate k-sequences from frequent k-1-sequences"""
        if self.verbose:
            logger.info(f"*** Generating candidate {k}-sequences ***")

        frequent_sequences_list = []
        for value in self.frequent_sequences.values():
            frequent_sequences_list.extend(value)

        n = len(self.db)

        if k == 2:
            for i, sequence1 in enumerate(frequent_sequences_list):
                for j in range(i, len(frequent_sequences_list)):
                    sequence2 = frequent_sequences_list[j]
                    event1 = sequence1.elements[0][0]
                    event2 = sequence2.elements[0][0]

                    """If the merged candidate has too few possible sequences
                    it could be contained in, it's immediately discarded
                    """
                    new_set_of_indexes = \
                        sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                    if len(new_set_of_indexes) / n < self.minsup:
                        continue

                    """Adds candidate [[event1], [event2]]"""
                    new_elements1 = [[event1], [event2]]

                    new_candidate1 = Sequence(new_elements1, new_set_of_indexes)
                    self.candidate_sequences.append(new_candidate1)

                    if self.verbose:
                        logger.info(f"{new_candidate1.elements}")

                    if event1 != event2:
                        """If the two events are different, add two more candidates:
                        [[event2], [event1]] and [[event1, event2]] (or [[event2, event1]])
                        """

                        """Adds candidate [[event2], [event1]]"""
                        new_elements2 = [[event2], [event1]]

                        new_candidate2 = Sequence(new_elements2, set(new_set_of_indexes))
                        self.candidate_sequences.append(new_candidate2)

                        """Adds [[event1, event2]] or [[event2, event1]], depending
                        on which is greater than the other
                        """
                        if event1 < event2:
                            new_elements3 = [[event1, event2]]
                        else:
                            new_elements3 = [[event2, event1]]

                        new_candidate3 = Sequence(new_elements3, set(new_set_of_indexes))
                        self.candidate_sequences.append(new_candidate3)

                        if self.verbose:
                            logger.info(f"{new_candidate2.elements}")
                            logger.info(f"{new_candidate3.elements}")

        else:
            for sequence1 in frequent_sequences_list:
                if len(sequence1.elements[0]) > 1:
                    starting_elem = 0
                    starting_event = 1
                else:
                    """If the first element has only one event, pick the first
                    event from the second element
                    """
                    starting_elem = 1
                    starting_event = 0

                key = sequence1.elements[starting_elem][starting_event]

                """Only the sequences that could potentially be merged with the
                current one get picked
                """
                if key not in self.frequent_sequences:
                    continue

                mergeable_candidates = self.frequent_sequences[key]
                for sequence2 in mergeable_candidates:
                    """If the merged candidate has too few possible sequences
                    it could be contained in, it's immediately discarded
                    """
                    new_set_of_indexes = \
                        sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                    if len(new_set_of_indexes) / n < self.minsup:
                        continue

                    if k == 3 or self.check_if_mergeable(sequence1.elements, sequence2.elements, starting_elem):
                        new_elements = deepcopy(sequence1.elements)

                        if len(sequence2.elements[-1]) == 1:
                            new_elements.append(list(sequence2.elements[-1]))
                        else:
                            new_elements[-1].append(sequence2.elements[-1][-1])

                        new_candidate = Sequence(new_elements, new_set_of_indexes)
                        self.candidate_sequences.append(new_candidate)

                        if self.verbose:
                            logger.info(f"{new_candidate.elements}")

    def check_if_mergeable(self, sequence1, sequence2, starting_elem1):
        """Check if k-1-sequence1 can be merged with k-1-sequence2 to produce a
        candidate k-sequence"""

        if starting_elem1 == 0:
            if sequence1[0][1:] != sequence2[0]:
                return False
            start = 1
        else:
            start = 0

        stop = len(sequence2) - 1
        for i in range(start, len(sequence1) - starting_elem1):
            if i == stop:
                break

            if sequence1[i + starting_elem1] != sequence2[i]:
                return False

        if len(sequence2[-1]) > 1:
            if sequence1[-1] != sequence2[-1][:-1]:
                return False

        return True

    def prune_candidates(self):
        """Prune all candidate k-sequences who contain at least one infrequent
        k-1-subsequence"""
        if self.verbose:
            logger.info("*** Pruning candidates ***")

        for candidate in list(self.candidate_sequences):
            if self.verbose:
                logger.info(f"Candidate: {candidate.elements}")

            """Skip check of subsequence obtained by removing first event from
            first element, it's always frequent
            """
            if len(candidate.elements[0]) > 1:
                starting_elem = 0
                starting_event = 1
            else:
                starting_elem = 1
                starting_event = 0

            key = candidate.elements[0][0]

            frequent_sequences_list = []
            for sequence in self.frequent_sequences[key]:
                frequent_sequences_list.append(sequence.elements)

            infrequent = False
            last_elem = len(candidate.elements) - 1
            last_event = len(candidate.elements[last_elem]) - 1
            for curr_elem in range(starting_elem, len(candidate.elements)):
                for curr_event in range(starting_event, len(candidate.elements[curr_elem])):

                    if (curr_elem == last_elem) and (curr_event == last_event):
                        """Skip check for subsequence obtained by removing last
                        event from last element, it's always frequent
                        """
                        break

                    """flag is used to mark whether a single event or a whole
                    element was removed from the candidate so it can be later
                    reinserted
                    """
                    if len(candidate.elements[curr_elem]) == 1:
                        popped_item = candidate.elements.pop(curr_elem)
                        flag = 0
                    else:
                        popped_item = candidate.elements[curr_elem].pop(curr_event)
                        flag = 1

                    if self.verbose:
                        logger.info(f"\tSubsequence: {candidate.elements}")

                    if candidate.elements not in frequent_sequences_list:
                        """If one of the k-1 subsequences is infrequent, the
                        candidate is pruned
                        """
                        if self.verbose:
                            logger.info("\tInfrequent")
                        infrequent = True
                        break

                    if flag:
                        candidate.elements[curr_elem].insert(curr_event, popped_item)
                    else:
                        candidate.elements.insert(curr_elem, popped_item)

                if infrequent:
                    break
                starting_event = 0

            if infrequent:
                self.candidate_sequences.remove(candidate)

    def support_count(self):
        """Calculate support count for all k-candidates, add all frequent ones
        to frequent_sequences"""
        if self.verbose:
            logger.info("*** Calculating support count ***")
            logger.info("*** Frequent sequences found: ***")

        n = len(self.db)
        for candidate in self.candidate_sequences:
            infrequent = False
            for index in list(candidate.set_of_indexes):
                if not self.is_contained(candidate.elements, self.db[index]):
                    candidate.set_of_indexes.discard(index)
                    if len(candidate.set_of_indexes) / n < self.minsup:
                        infrequent = True
                        break
            if infrequent:
                continue

            self.frequent_sequences[candidate.elements[0][0]].append(candidate)

            if self.verbose:
                logger.info(f"Sequence: {candidate.elements}")
                logger.info(f"Support count: {len(candidate.set_of_indexes)}")

        """Keys that correspond to an empty list are removed from frequent_sequences"""
        for event in list(self.frequent_sequences):
            if not self.frequent_sequences[event]:
                del self.frequent_sequences[event]

    def is_contained(self, c, s):
        """Check if candidate c is contained in sequence s"""
        if self.verbose:
            logger.info(f"Checking if {c} is in {s}")

        i = 0
        for s_element in s:
            if self.verbose:
                logger.info(f"Checking elements: {c[i]} in {s_element}")

            if all(event in s_element for event in c[i]):
                if self.verbose:
                    logger.info(f"Yes")

                i += 1
                if i == len(c):
                    return True
        return False

    def print_frequent_sequences(self):
        """Add current frequent sequences to output list"""
        for sequence_list in self.frequent_sequences.values():
            for sequence in sequence_list:
                self.output.append((sequence.elements, len(sequence.set_of_indexes)))


def load_db(input_filename):
    """Return the sequence database contained in input_filename"""
    try:
        path = open(input_filename, 'r')
    except FileNotFoundError:
        print("File", input_filename, "not found.")
        return []

    content = path.read()
    strings = content.split()

    database = []
    sequence = []
    element = []

    for string in strings:
        if string == "-2":
            """String marks end of sequence"""
            database.append(sequence)
            sequence = []
            element = []
        elif string == "-1":
            """String marks end of element"""
            sequence.append(element)
            element = []
        else:
            """String is an event"""
            event = int(string)
            element.append(event)
    path.close()
    return database


class Sequence:
    """A class that models a sequence.
    """

    def __init__(self, elements, set_of_indexes):
        self.elements = elements
        self.set_of_indexes = set_of_indexes

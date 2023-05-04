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

        if not verbose:
            logger.disabled = True

        """Find all unique events (1-sequences)"""
        for i in range(len(self.db)):
            for element in self.db[i]:
                for event in element:
                    if event not in self.frequent_sequences:
                        self.frequent_sequences[event] = [Sequence([[event]], set())]
                    self.frequent_sequences[event][0].set_of_indexes.add(i)

    def run_gsp(self):
        """Run GSP algorithm"""
        logger.info("STARTING GSP ALGORITHM\n")
        logger.info("*** Finding all frequent 1-sequences ***")

        """Find all frequent 1-sequences"""
        for event in list(self.frequent_sequences.keys()):
            support_count = len(self.frequent_sequences[event][0].set_of_indexes)
            support = support_count / len(self.db)
            if support < self.minsup:
                del self.frequent_sequences[event]
            else:
                logger.info(f"Event: {event} - Support count: {support_count}")

        k = 2
        """Loop until there are no more frequent k-sequences"""
        while self.frequent_sequences:
            """All frequent k-1-sequences get printed to the output file"""
            self.print_frequent_sequences()

            """Generate and prune all candidate k-sequences"""
            self.generate_candidates(k)
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
        logger.info(f"*** Generating candidate {k}-sequences ***")

        frequent_sequences_list = []
        for value in self.frequent_sequences.values():
            if value:
                frequent_sequences_list.extend(value)

        if k == 2:
            for i in range(len(frequent_sequences_list)):
                for j in range(i, len(frequent_sequences_list)):
                    sequence1 = frequent_sequences_list[i]
                    sequence2 = frequent_sequences_list[j]
                    event1 = sequence1.elements[0][0]
                    event2 = sequence2.elements[0][0]

                    """Adds candidate [[event1], [event2]]"""
                    new_elements1 = [[event1], [event2]]
                    new_set_of_indexes1 =\
                        sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)

                    new_candidate1 = Sequence(new_elements1, new_set_of_indexes1)
                    self.candidate_sequences.append(new_candidate1)

                    logger.info(f"{new_candidate1.elements}")

                    """If the two events are different, add two more candidates:
                    [[event2], [event1]] and [[event1, event2]] (or [[event2, event1]])
                    """
                    if event1 != event2:
                        """Adds candidate [[event2], [event1]]"""
                        new_elements2 = [[event2], [event1]]
                        new_set_of_indexes2 = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)

                        new_candidate2 = Sequence(new_elements2, new_set_of_indexes2)
                        self.candidate_sequences.append(new_candidate2)

                        logger.info(f"{new_candidate2.elements}")

                        """Adds [[event1, event2]] or [[event2, event1]], depending
                        on which is greater than the other
                        """
                        if event1 < event2:
                            new_elements3 = [[event1, event2]]
                        else:
                            new_elements3 = [[event2, event1]]
                        new_set_of_indexes3 = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)

                        new_candidate3 = Sequence(new_elements3, new_set_of_indexes3)
                        self.candidate_sequences.append(new_candidate3)

                        logger.info(f"{new_candidate3.elements}")

        else:
            for sequence1 in frequent_sequences_list:
                if len(sequence1.elements[0]) > 1:
                    starting_elem = 0
                    starting_event = 1
                    key = sequence1.elements[0][1]
                else:
                    """If the first element has only one event, pick the first
                    event from the second element
                    """
                    starting_elem = 1
                    starting_event = 0
                    key = sequence1.elements[1][0]

                """Only the sequences that could potentially be merged with the
                current one get picked
                """
                if key not in self.frequent_sequences:
                    continue

                mergeable_candidates = self.frequent_sequences[key]

                for sequence2 in mergeable_candidates:
                    if self.check_if_mergeable(sequence1.elements, sequence2.elements, starting_elem, starting_event):
                        new_elements = deepcopy(sequence1.elements)

                        last = len(sequence2.elements) - 1

                        if len(sequence2.elements[last]) == 1:
                            new_elements.append(deepcopy(sequence2.elements[last]))
                        else:
                            new_elements[len(new_elements) - 1].append(
                                sequence2.elements[last][len(sequence2.elements[last]) - 1])

                        new_set_of_indexes = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)

                        new_candidate = Sequence(new_elements, new_set_of_indexes)
                        self.candidate_sequences.append(new_candidate)

                        logger.info(f"{new_candidate.elements}")

    def check_if_mergeable(self, sequence1, sequence2, curr_elem1, curr_event1):
        """Check if k-1-sequence1 can be merged with k-1-sequence2 to produce a
        candidate k-sequence"""
        curr_elem2 = 0
        curr_event2 = 0
        while curr_elem1 < len(sequence1):
            while (curr_event1 < len(sequence1[curr_elem1])) &\
                    (curr_event2 < len(sequence2[curr_elem2])):
                if sequence1[curr_elem1][curr_event1] != \
                        sequence2[curr_elem2][curr_event2]:
                    return False

                curr_event1 += 1
                curr_event2 += 1

            if (curr_event1 != len(sequence1[curr_elem1])) | \
                    ((curr_event2 != len(sequence2[curr_elem2])) &
                     (curr_elem1 != len(sequence1) - 1)):
                """Either one of the current elements has more events than the
                other (the only exception allowed is if the current element is
                the last one)
                """
                return False
            curr_event1 = 0
            curr_event2 = 0

            curr_elem1 += 1
            curr_elem2 += 1
        return True

    def prune_candidates(self):
        """Prune all candidate k-sequences who contain at least one infrequent
        k-1-subsequence"""
        logger.info("*** Pruning candidates ***")

        for candidate in list(self.candidate_sequences):
            logger.info(f"Candidate: {candidate.elements}")

            """Skip check of subsequence obtained by removing first event from
            fist element
            """
            if len(candidate.elements[0]) > 1:
                starting_elem = 0
                starting_event = 1
            else:
                starting_elem = 1
                starting_event = 0

            key = candidate.elements[0][0]

            """If no frequent sequences starting with the candidate's 2nd event
            are found, skip subsequence generation
            """
            if key not in self.frequent_sequences:
                logger.info("No frequent subsequences found")
                self.candidate_sequences.remove(candidate)
                continue

            frequent_sequences_list = []
            for sequence in self.frequent_sequences[key]:
                frequent_sequences_list.append(sequence.elements)

            infrequent = False
            for curr_elem in range(starting_elem, len(candidate.elements)):
                for curr_event in range(starting_event, len(candidate.elements[curr_elem])):
                    subsequence = deepcopy(candidate.elements)

                    if len(subsequence[curr_elem]) == 1:
                        subsequence.pop(curr_elem)
                    else:
                        subsequence[curr_elem].pop(curr_event)

                    logger.info(f"\tSubsequence: {subsequence}")

                    if subsequence not in frequent_sequences_list:
                        """If one of the k-1 subsequences is infrequent, the
                        candidate is pruned
                        """
                        logger.info("\tInfrequent")
                        infrequent = True
                        break
                    else:
                        logger.info("\tFrequent")

                    if (curr_elem == len(candidate.elements) - 1) & \
                            (curr_event == len(candidate.elements[curr_elem]) - 1):
                        """Skip check for subsequence obtained by removing last
                        event from last element
                        """
                        break
                    curr_event += 1

                if infrequent:
                    break
                starting_event = 0

            if infrequent:
                self.candidate_sequences.remove(candidate)

    def support_count(self):
        """Calculate support count for all k-candidates, add all frequent ones
        to frequent_sequences"""
        logger.info("*** Calculating support count ***")

        for candidate in self.candidate_sequences:
            for index in list(candidate.set_of_indexes):
                if not self.is_contained(candidate.elements, self.db[index]):
                    candidate.set_of_indexes.discard(index)

        logger.info("*** Frequent sequences found: ***")

        for candidate in self.candidate_sequences:
            support_count = len(candidate.set_of_indexes)
            support = support_count / len(self.db)
            if support >= self.minsup:
                self.frequent_sequences[candidate.elements[0][0]].append(candidate)

                logger.info(f"Sequence: {candidate.elements}")
                logger.info(f"Support count: {support_count}")

        """Keys which correspond to an empty list are removed from frequent_sequences"""
        for event in list(self.frequent_sequences.keys()):
            if not self.frequent_sequences[event]:
                del self.frequent_sequences[event]

    def is_contained(self, c, s):
        """Check if candidate c is contained in sequence s"""
        i = 0
        j = 0
        while (i < len(c)) & (j < len(s)):
            k = 0
            h = 0
            while (k < len(c[i])) & (h < len(s[j])):
                if c[i][k] == s[j][h]:
                    k += 1
                h += 1
            if k == len(c[i]):
                i += 1
            j += 1
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

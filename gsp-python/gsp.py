from copy import deepcopy
import math
import logging

"""Logger for tracking execution on stdout"""
logger = logging.getLogger(__name__)


class GSP:
    """A class that implements the Generalized Sequential Pattern algorithm.

    An instance of the GSP class runs the GSP algorithm on a sequence dataset,
    mining all frequent sequences in the dataset whose support is higher or
    equal than a minimum threshold.
    """

    def __init__(self, ds, minsup, max_k=math.inf, maxgap=math.inf, mingap=0, maxspan=math.inf, verbose=False):
        """Initialize an instance of the class with a reference to the dataset
        from which frequent sequences must be mined and a minsupport threshold,
        and maxgap/mingap/maxspan time constraints.
        """
        self.ds = ds
        self.minsup = minsup
        self.maxgap = maxgap
        self.mingap = mingap
        self.maxspan = maxspan

        self.frequent_sequences = {}
        self.candidate_sequences = []

        self.max_k = max_k

        self.verbose = verbose
        if not verbose:
            logger.disabled = True

        """Find all unique events (1-sequences)"""
        for index, sequence in enumerate(self.ds):
            for element in sequence:
                for event in element:
                    if event not in self.frequent_sequences:
                        self.frequent_sequences[event] = [Sequence([[event]], set())]
                    self.frequent_sequences[event][0].set_of_indexes.add(index)

    def run_gsp(self):
        output = []

        """Run GSP algorithm"""
        if self.verbose:
            logger.info("STARTING GSP ALGORITHM\n")
            logger.info("*** Finding all frequent 1-sequences ***")

        """Find all frequent 1-sequences"""
        n = len(self.ds)
        for event in list(self.frequent_sequences):
            support_count = len(self.frequent_sequences[event][0].set_of_indexes)
            support = support_count / n
            if support < self.minsup:
                del self.frequent_sequences[event]
            else:
                if self.verbose:
                    logger.info(f"Event: {event} - Support count: {support_count}")
        self.add_frequent_sequences(output)

        k = 2
        """Loop until there are no more frequent k-sequences"""
        while self.frequent_sequences and (k <= self.max_k):
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

            """All frequent k-1-sequences get printed to the output"""
            self.add_frequent_sequences(output)

            k += 1

        return output

    def generate_candidates(self, k):
        """Generate all candidate k-sequences from frequent k-1-sequences"""
        if self.verbose:
            logger.info(f"*** Generating candidate {k}-sequences ***")

        frequent_sequences_list = []
        for value in self.frequent_sequences.values():
            frequent_sequences_list.extend(value)

        n = len(self.ds)

        if k == 2:
            for i, sequence1 in enumerate(frequent_sequences_list):
                for j in range(i, len(frequent_sequences_list)):
                    sequence2 = frequent_sequences_list[j]
                    event1 = sequence1.elements[0][0]
                    event2 = sequence2.elements[0][0]

                    if event1 == event2:
                        new_set_of_indexes = sequence1.set_of_indexes
                    else:
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
                    key = sequence1.elements[0][1]
                    starting_elem = 0
                else:
                    """If the first element has only one event, pick the first
                    event from the second element
                    """
                    key = sequence1.elements[1][0]
                    starting_elem = 1

                """Only the sequences that could potentially be merged with the
                current one get picked
                """
                if key not in self.frequent_sequences:
                    continue

                for sequence2 in self.frequent_sequences[key]:
                    if k == 3 or self.check_if_mergeable(sequence1.elements, sequence2.elements, starting_elem):
                        """If the merged candidate has too few possible sequences
                        it could be contained in, it's immediately discarded
                        """
                        new_set_of_indexes = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                        if len(new_set_of_indexes) / n < self.minsup:
                            continue

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
        if len(sequence1) == 1 and len(sequence2) == 1:
            if sequence1[0][1:] != sequence2[0][:-1]:
                return False
            return True

        if starting_elem1 == 0:
            if sequence1[0][1:] != sequence2[0]:
                return False
            start = 1
        else:
            start = 0

        for i in range(start, len(sequence2) - 1):
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

        """Maxgap constraint violates Apriori principle, if a value is given
        for it, pruning strategy must be chosen accordingly
        """
        if self.maxgap == math.inf:
            prune = self.prune_without_time_constraints
        else:
            prune = self.prune_with_time_constraints

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

            if not prune(candidate.elements, starting_elem, starting_event, frequent_sequences_list):
                self.candidate_sequences.remove(candidate)

    def prune_without_time_constraints(self, candidate, starting_elem, starting_event, frequent_sequences_list):
        """Check if candidate sequence contains at least one infrequent
        subsequence
        """

        last_elem = len(candidate)
        for curr_elem in range(starting_elem, last_elem):
            last_event = len(candidate[curr_elem])
            for curr_event in range(starting_event, last_event):
                if (curr_elem == last_elem - 1) and (curr_event == last_event - 1):
                    """Skip check for subsequence obtained by removing last
                    event from last element, it's always frequent
                    """
                    return True

                """flag is used to mark whether a single event or a whole
                element was removed from the candidate so it can be later
                reinserted
                """
                if last_event == 1:
                    popped_item = candidate.pop(curr_elem)
                else:
                    popped_item = candidate[curr_elem].pop(curr_event)

                if self.verbose:
                    logger.info(f"\tSubsequence: {candidate}")

                if candidate not in frequent_sequences_list:
                    """If one of the k-1 subsequences is infrequent, the
                    candidate is pruned
                    """
                    if self.verbose:
                        logger.info("\tInfrequent")
                    return False

                if last_event == 1:
                    candidate.insert(curr_elem, popped_item)
                else:
                    candidate[curr_elem].insert(curr_event, popped_item)
            starting_event = 0

        if self.verbose:
            logger.info("\tAll subsequences are frequent")
        return True

    def prune_with_time_constraints(self, candidate, starting_elem, starting_event, frequent_sequences_list):
        """Check if candidate sequence contains at least one infrequent
        contiguous subsequence
        """

        last_elem = len(candidate)
        for curr_elem in range(starting_elem, last_elem):
            if len(candidate[curr_elem]) == 1:
                """If element has only one event, skip its removal"""
                continue

            last_event = len(candidate[curr_elem])
            for curr_event in range(starting_event, last_event):
                if (curr_elem == last_elem - 1) and (curr_event == last_event - 1):
                    """Skip check for subsequence obtained by removing last
                    event from last element, it's always frequent
                    """
                    return True

                popped_item = candidate[curr_elem].pop(curr_event)

                if self.verbose:
                    logger.info(f"\tSubsequence: {candidate}")

                if candidate not in frequent_sequences_list:
                    """If one of the k-1 subsequences is infrequent, the
                    candidate is pruned
                    """
                    if self.verbose:
                        logger.info("\tInfrequent")
                    return False

                candidate[curr_elem].insert(curr_event, popped_item)
            starting_event = 0

        if self.verbose:
            logger.info("\tAll contiguous subsequences are frequent")
        return True

    def support_count(self):
        """Calculate support count for all k-candidates, add all frequent ones
        to frequent_sequences
        """
        if self.verbose:
            logger.info("*** Calculating support count ***")
            logger.info("*** Frequent sequences found: ***")

        if (self.maxgap == math.inf) and (self.mingap == 0) and (self.maxspan == math.inf):
            is_contained = self.is_contained_without_time_constraints
        else:
            is_contained = self.is_contained_with_time_constraints

        n = len(self.ds)
        for candidate in self.candidate_sequences:
            infrequent = False
            for index in list(candidate.set_of_indexes):
                if not is_contained(candidate.elements, self.ds[index]):
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

        """Keys paired to an empty list are removed from frequent_sequences"""
        for event in list(self.frequent_sequences):
            if not self.frequent_sequences[event]:
                del self.frequent_sequences[event]

    def is_contained_without_time_constraints(self, c, s):
        """Check if candidate c is contained in sequence s"""
        if self.verbose:
            logger.info(f"Checking if {c} is in {s}")

        c_iter = iter(c)
        c_element = next(c_iter)
        for s_element in s:
            if self.verbose:
                logger.info(f"Checking elements: {c_element} in {s_element}")

            if set(c_element).issubset(s_element):
                if self.verbose:
                    logger.info(f"Yes")

                if not (c_element := next(c_iter, [])):
                    """If next returns empty list (default value), all of the
                    elements of the candidate have been found
                    """
                    return True
        return False

    def is_contained_with_time_constraints(self, c, s):
        """Check if candidate c is contained in sequence s"""
        if self.verbose:
            logger.info(f"Checking if {c} is in {s}")

        for start, s_element in enumerate(s):
            """Check starts at first occurrence of the candidate's first element;
            if not found, check continues from next occurrence
            """
            if set(c[0]).issubset(s_element):
                """Start of ''Forward phase'' from first element"""
                if self.verbose:
                    logger.info(f"Found {c[0]} at index {start}")

                gap = 0
                j = 1
                i = start + 1
                """last_found and last_gap are used to recover information
                about the state of the check for the previous element
                """
                last_found = 0
                last_gap = 0

                while i < len(s) and j < len(c):

                    gap += 1

                    if (i - start) > self.maxspan:
                        """Start of ''backward phase'' for maxspan violation,
                        check has to restart from the candidate's first
                        element
                        """
                        if self.verbose:
                            logger.info("maxspan constraint violated")
                            break

                    if gap > self.maxgap:
                        """Start of ''backward phase'' for maxgap violation"""
                        if self.verbose:
                            logger.info("maxgap constraint violated")

                        if j == 1:
                            """Current element is the second one, restart search
                            from first (outside of loop)
                            """
                            break
                        j -= 1
                        i = last_found + 1
                        gap = last_gap
                        continue

                    if self.verbose:
                        logger.info(f"Checking {c[j]} in {s[i]}")

                    if set(c[j]).issubset(s[i]) and (gap > self.mingap):
                        last_found = i
                        last_gap = gap
                        gap = 0
                        j += 1
                    i += 1

                if j == len(c):
                    return True
        return False

    def add_frequent_sequences(self, output):
        """Add current frequent sequences to output list"""
        for sequence_list in self.frequent_sequences.values():
            for sequence in sequence_list:
                output.append((sequence.elements, len(sequence.set_of_indexes)))


def load_ds(input_filename):
    """Return the sequence dataset contained in input_filename, converting
    all events found to integers
    """
    try:
        path = open(input_filename, 'r')
    except FileNotFoundError:
        print("File", input_filename, "not found.")
        return [], {}, {}

    str_to_int_dict = {}
    int_to_str_dict = {}

    dataset = []
    sequence = []
    element = []

    integer_conv = 1

    for line in path:
        for string in line.split():
            if string == "-2":
                """String marks end of sequence"""
                dataset.append(sequence)
                sequence = []
                element = []
            elif string == "-1":
                """String marks end of element"""
                sequence.append(element)
                element = []
            else:
                """String is an event"""
                if string not in str_to_int_dict:
                    str_to_int_dict[string] = integer_conv
                    int_to_str_dict[integer_conv] = string
                    integer_conv += 1
                event = str_to_int_dict[string]
                element.append(event)

    path.close()
    return dataset, int_to_str_dict, str_to_int_dict


class Sequence:
    """A class that models a sequence.
    """

    def __init__(self, elements, set_of_indexes):
        """Initialize an instance of the class with a reference to the elements
        of the sequence and the set of dataset indexes corresponding to the
        dataset sequences the sequence could appear in
        """
        self.elements = elements
        self.set_of_indexes = set_of_indexes

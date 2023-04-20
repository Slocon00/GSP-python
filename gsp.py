from pathlib import Path
from copy import deepcopy


class GSP:

    def __init__(self, db, output_filename, minsup):
        self.db = db
        self.minsup = minsup
        self.frequent_sequences = {}
        self.candidate_sequences = []
        self.output_path = Path(output_filename)

        for i in range(len(self.db)):
            for element in self.db[i]:
                for event in element:
                    if event not in self.frequent_sequences:
                        self.frequent_sequences[event] = [Sequence()]
                        self.frequent_sequences[event][0].elements.append([event])
                    self.frequent_sequences[event][0].set_of_indexes.add(i)

    def run_gsp(self):
        """Find all frequent 1-sequences"""
        for event in self.frequent_sequences:
            support_count = len(self.frequent_sequences[event][0].set_of_indexes)
            support = support_count / len(self.db)
            if support < self.minsup:
                self.frequent_sequences[event].clear()

        k = 2
        """Loop until there are no more frequent k-sequences"""
        # while self.frequent_sequences:
        self.print_frequent_sequences()

        self.generate_candidates(k)
        self.candidate_sequences.clear()

    def generate_candidates(self, k):
        """Generate all candidate k-sequences from frequent k-1-sequences"""
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
                    new_candidate1 = Sequence()
                    new_candidate1.elements.append([event1])
                    new_candidate1.elements.append([event2])
                    new_candidate1.set_of_indexes = \
                        sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                    self.candidate_sequences.append(new_candidate1)

                    """If the two events are different, add two more candidates:
                    [[event2], [event1]] and [[event1, event2]] (or [[event2, event1]])
                    """
                    if event1 != event2:
                        new_candidate2 = Sequence()
                        new_candidate3 = Sequence()

                        """Adds candidate [[event2], [event1]]"""
                        new_candidate2.elements.append([event2])
                        new_candidate2.elements.append([event1])
                        new_candidate2.set_of_indexes = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                        self.candidate_sequences.append(new_candidate2)

                        """Adds [[event1, event2]] or [[event2, event1]], depending
                        on which is greater than the other
                        """
                        if event1 < event2:
                            new_candidate3.elements.append([event1, event2])
                        else:
                            new_candidate3.elements.append([event2, event1])
                        new_candidate3.set_of_indexes = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                        self.candidate_sequences.append(new_candidate3)
        else:
            for sequence1 in frequent_sequences_list:
                if len(sequence1.elements[0]) > 1:
                    istart = 0
                    jstart = 1
                    key = sequence1.elements[0][1]
                else:
                    """If the first element has only one event, pick the first
                    event from the second element
                    """
                    istart = 1
                    jstart = 0
                    key = sequence1.elements[1][0]

                """Only the sequences that could potentially be merged with the
                current one get picked
                """
                mergeable_candidates = self.frequent_sequences[key]

                for sequence2 in mergeable_candidates:

                    if self.check_if_mergeable(sequence1, sequence2, istart, jstart):
                        new_candidate = Sequence()
                        new_candidate.elements = deepcopy(sequence1.elements)

                        len_of_snd = len(sequence2.elements)

                        if len(sequence2.elements[len_of_snd - 1]) == 1:
                            new_candidate.elements.append(deepcopy(sequence2.elements[len_of_snd - 1]))
                        else:
                            new_candidate.elements[len(new_candidate.elements) - 1].append(
                                sequence2.elements[len_of_snd - 1][len(sequence2.elements[len_of_snd - 1]) - 1])

                        new_candidate.set_of_indexes = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                        self.candidate_sequences.append(new_candidate)
                        print(new_candidate.elements)

    def check_if_mergeable(self, sequence1, sequence2, i, j):
        """Check if k-1-sequence1 can be merged with k-1-sequence2 to produce a
        candidate k-sequence"""
        m = 0
        n = 0
        while i < len(sequence1.elements):
            while (j < len(sequence1.elements[i])) & (n < len(sequence2.elements[m])):
                if sequence1.elements[i][j] != sequence2.elements[m][n]:
                    return False
                j += 1
                n += 1
            if (j != len(sequence1.elements[i])) | \
                    ((n != len(sequence2.elements[m])) & (i != len(sequence1.elements) - 1)):
                return False
            j = 0
            n = 0
            i += 1
            m += 1
        return True

    def prune_candidates(self):
        """Prune all candidate k-sequences who contain at least one infrequent
        k-1-subsequence"""
        pass

    def support_count(self):
        """Calculate support count for all k-candidates, add all frequent ones
        to frequent_sequences"""
        pass

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
        """Print current frequent sequences to output file"""
        content = ""
        for sequence_list in self.frequent_sequences.values():
            for sequence in sequence_list:
                content += f"{sequence.elements} : {len(sequence.set_of_indexes)}\n"

        self.output_path.write_text(content)


def load_db(input_filename):
    """Return the sequence database contained in input_filename"""
    path = Path(input_filename)
    try:
        content = path.read_text()
    except FileNotFoundError:
        print("File", input_filename, "not found.")
        return []

    chars = content.split()
    database = []
    sequence = []
    element = []

    index = 0
    for char in chars:
        if char == "-2":
            """Character marks end of sequence"""
            database.append(sequence)
            sequence = []
            element = []
            index += 1
        elif char == "-1":
            """Character marks end of element"""
            sequence.append(element)
            element = []
        else:
            """Character is an event"""
            event = int(char)
            element.append(event)

    return database


class Sequence:

    def __init__(self):
        self.elements = []
        self.set_of_indexes = set()

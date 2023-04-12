from pathlib import Path
from copy import deepcopy


class GSP:

    def __init__(self):
        self.db = []
        self.frequent_sequences = {}
        self.candidate_sequences = []

    def run_gsp(self, input_filename, output_filename, minsup):
        """Run GSP algorithm with the given minsup parameter"""
        if not self.load_db(input_filename):
            return

        output_path = Path(output_filename)
        if output_path.exists():
            print("File", output_filename, "already exists, want to proceed? [Y/N]")
            answer = ""
            while (answer != "Y") & (answer != "N"):
                answer = input()

            if answer == "N":
                return

        """Find all frequent 1-sequences"""
        for item in self.frequent_sequences:
            support_count = len(self.frequent_sequences[item][0].set_of_indexes)
            support = support_count / len(self.db)
            if support < minsup:
                self.frequent_sequences[item].clear()

        self.print_frequent_sequences(output_path)

        k = 2
        """Loop until there are no more frequent k-sequences"""
        # while self.frequent_sequences:
        self.candidate_sequences.clear()
        self.generate_candidates(k)

        for item in self.frequent_sequences:
            self.frequent_sequences[item].clear()
        for seq in self.candidate_sequences:
            self.frequent_sequences[seq.itemsets[0][0]].append(seq)
        self.candidate_sequences.clear()
        self.generate_candidates(3)

        for item in self.frequent_sequences:
            self.frequent_sequences[item].clear()
        for seq in self.candidate_sequences:
            self.frequent_sequences[seq.itemsets[0][0]].append(seq)
        self.candidate_sequences.clear()
        self.generate_candidates(4)

        for item in self.frequent_sequences:
            self.frequent_sequences[item].clear()
        for seq in self.candidate_sequences:
            self.frequent_sequences[seq.itemsets[0][0]].append(seq)

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
                    item1 = sequence1.itemsets[0][0]
                    item2 = sequence2.itemsets[0][0]

                    """Adds candidate [[item1], [item2]]"""
                    new_candidate1 = Sequence()
                    new_candidate1.itemsets.append([item1])
                    new_candidate1.itemsets.append([item2])
                    new_candidate1.set_of_indexes = \
                        sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                    self.candidate_sequences.append(new_candidate1)

                    """If the two items are different, add two more candidates:
                    [[item2], [item1]] and [[item1, item2]] (or [[item2, item1]])
                    """
                    if item1 != item2:
                        new_candidate2 = Sequence()
                        new_candidate3 = Sequence()

                        """Adds candidate [[item2], [item1]]"""
                        new_candidate2.itemsets.append([item2])
                        new_candidate2.itemsets.append([item1])
                        new_candidate2.set_of_indexes = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                        self.candidate_sequences.append(new_candidate2)

                        """Adds [[item1, item2]] or [[item2, item1]], depending
                        on which is greater than the other
                        """
                        if item1 < item2:
                            new_candidate3.itemsets.append([item1, item2])
                        else:
                            new_candidate3.itemsets.append([item2, item1])
                        new_candidate3.set_of_indexes = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                        self.candidate_sequences.append(new_candidate3)
        else:
            for sequence1 in frequent_sequences_list:
                if len(sequence1.itemsets[0]) > 1:
                    istart = 0
                    jstart = 1
                    key = sequence1.itemsets[0][1]
                else:
                    """If the first itemset has only one item, pick the first
                    item from the second itemset
                    """
                    istart = 1
                    jstart = 0
                    key = sequence1.itemsets[1][0]

                """Only the sequences that could potentially be merged with the
                current one get picked
                """
                mergeable_candidates = self.frequent_sequences[key]

                for sequence2 in mergeable_candidates:
                    print(sequence1.itemsets, "con", sequence2.itemsets)

                    if self.check_if_mergeable(sequence1, sequence2, istart, jstart):
                        new_candidate = Sequence()
                        new_candidate.itemsets = deepcopy(sequence1.itemsets)

                        len_of_snd = len(sequence2.itemsets)

                        if len(sequence2.itemsets[len_of_snd - 1]) == 1:
                            new_candidate.itemsets.append(deepcopy(sequence2.itemsets[len_of_snd - 1]))
                        else:
                            new_candidate.itemsets[len(new_candidate.itemsets) - 1].append(
                                sequence2.itemsets[len_of_snd - 1][len(sequence2.itemsets[len_of_snd - 1]) - 1])

                        new_candidate.set_of_indexes = \
                            sequence1.set_of_indexes.intersection(sequence2.set_of_indexes)
                        self.candidate_sequences.append(new_candidate)
                        print("produce", new_candidate.itemsets)

    def check_if_mergeable(self, sequence1, sequence2, i, j):
        """Check if k-1-sequence1 can be merged with k-1-sequence2 to produce a
        candidate k-sequence"""
        m = 0
        n = 0
        while i < len(sequence1.itemsets):
            while (j < len(sequence1.itemsets[i])) & (n < len(sequence2.itemsets[m])):
                if sequence1.itemsets[i][j] != sequence2.itemsets[m][n]:
                    return False
                j += 1
                n += 1
            if (j != len(sequence1.itemsets[i])) | \
                    ((n != len(sequence2.itemsets[m])) & (i != len(sequence1.itemsets) - 1)):
                return False
            j = 0
            n = 0
            i += 1
            m += 1
        return True

    def prune_candidates(self):
        pass

    def load_db(self, input_filename):
        """Store in db the sequence database contained in input_filename"""
        path = Path(input_filename)
        try:
            content = path.read_text()
        except FileNotFoundError:
            print("File", input_filename, "not found.")
            return False

        chars = content.split()
        sequence = []
        element = []

        index = 0
        for char in chars:
            if char == "-2":
                """Character marks end of sequence"""
                self.db.append(sequence)
                sequence = []
                element = []
                index += 1
            elif char == "-1":
                """Character marks end of element"""
                sequence.append(element)
                element = []
            else:
                """Character is an item"""
                item = int(char)
                element.append(item)

                if item not in self.frequent_sequences:
                    self.frequent_sequences[item] = [Sequence()]
                    self.frequent_sequences[item][0].itemsets.append([item])
                self.frequent_sequences[item][0].set_of_indexes.add(index)

        return True

    def print_frequent_sequences(self, output_path):
        """Print current frequent sequences to output file"""
        content = ""
        for sequence_list in self.frequent_sequences.values():
            for sequence in sequence_list:
                content += f"{sequence.itemsets} : {len(sequence.set_of_indexes)}\n"

        output_path.write_text(content)


class Sequence:

    def __init__(self):
        self.itemsets = []
        self.set_of_indexes = set()

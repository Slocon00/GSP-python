from pathlib import Path


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

    def generate_candidates(self, k):
        """Generate all candidate k-sequences from frequent k-1-sequences"""
        if k == 2:
            frequent_items = []
            for value in self.frequent_sequences.values():
                if value:
                    frequent_items.extend(value)

            for i in range(len(frequent_items)):
                for j in range(i, len(frequent_items)):
                    sequence1 = frequent_items[i]
                    sequence2 = frequent_items[j]
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
            pass

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

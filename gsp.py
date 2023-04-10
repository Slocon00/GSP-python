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

    def generate_candidates(self):
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


class Sequence:

    def __init__(self):
        self.itemsets = []
        self.set_of_indexes = set()
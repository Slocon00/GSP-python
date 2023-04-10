from pathlib import Path


class GSP:

    def __init__(self):
        self.db = []

    def run_gsp(self, input_filename, output_filename, minsup):
        """Run GSP algorithm with the given minsup parameter"""
        if not self.load_db(input_filename):
            return

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

        for char in chars:
            if char == "-2":
                """Character marks end of sequence"""
                self.db.append(sequence)
                sequence = []
                element = []
            elif char == "-1":
                """Character marks end of element"""
                sequence.append(element)
                element = []
            else:
                """Character is an item"""
                item = int(char)
                element.append(item)

        return True

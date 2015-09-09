from collections import defaultdict
import random


class Vocab:
    def __init__(self, words=None, stride=3):
        # handle roots separate from the rest of the bag-of-letters for much improved results
        self.roots = defaultdict(list)
        self.root_list = []
        self.links = defaultdict(list)

        self.stride = stride

        if words:
            self.ingest(words)

    def ingest(self, words):
        for word in words:
            chunks = [word[i:i+self.stride] for i in range(0, len(word))]

            root_chunk = chunks.pop(0)

            if len(root_chunk) != self.stride:
                continue

            root = self.roots[root_chunk]
            self.root_list.append(root_chunk)

            chunk = chunks.pop(0)

            if len(chunk) == self.stride:
                root.append(chunk[-1])
            else:
                root.append('\n')
                continue

            while chunks:
                next_chunk = chunks.pop(0)

                if len(next_chunk) == self.stride:
                    self.links[chunk].append(next_chunk[-1])
                else:
                    self.links[chunk].append('\n')
                    break

                chunk = next_chunk

    def init_word(self):
        root = random.choice(self.root_list)

        word = list(root)
        word.append(random.choice(self.roots[root]))

        return word

    def generate(self, max_length=15, num_retries=30):
        for _retry in range(num_retries):  # retry a few times to stay under max_length
            word = self.init_word()

            while len(word) < max_length:
                if word[-1] == '\n':
                    return ''.join(word).strip()

                choices = self.links[''.join(word[-self.stride:])]
                word.append(random.choice(choices))

        raise RuntimeError("Failed to generate a word {} times in a row".format(num_retries))


if __name__ == '__main__':
    from urllib.request import urlopen

    def names_from_census(url):
        names = []

        data = urlopen(url).read().decode('utf-8')
        for line in data.split('\n'):
            data = line.split(' ', 1)
            if data and data[0]:
                names.append(data[0].title())

        return names

    female = Vocab(
        names_from_census('http://deron.meranda.us/data/census-dist-female-first.txt')
    )

    for x in range(3000):
        print(female.generate())

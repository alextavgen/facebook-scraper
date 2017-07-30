# char level markov chain text generator

import random
import time
import json
import string
import random

class TextGeneratorCharacter:

    def __init__(self):
        self.model = {}
        self.full_text = ''
        self.order = 0

    # load file to one string and strip newline chars/extra spaces..
    # may want to change everything to line by line for large input
    def read_file(self, file_name):
        with open(file_name, 'r') as f:
            self.full_text = ' '.join(line.rstrip() for line in f)

    def load_model(self, file_name):
        with open(file_name, 'r') as f:
            self.model = json.load(f)

    def save_model(self, file_name):
        with open(file_name, 'w') as out:
            json.dump(self.model, out, sort_keys=True, indent=4)

    # create markov model of specified order
    def train_model(self, order):
        self.order = order
        for i in range(0, len(self.full_text)-order):

            if i % 10000 == 0:
                print str(i) + ' characters trained'

            substring = self.full_text[i:(i+order)]
            next_char = self.full_text[i + order]

            if substring not in self.model.keys():
                self.model[substring] = {next_char: 1}
            else:
                if next_char not in self.model[substring].keys():
                    self.model[substring][next_char] = 1
                else:
                    self.model[substring][next_char] += 1

    # generate text of specified length based on the model, with first <order>
    # characters as the seed should prob add check to make sure model has been made
    def generate_text(self, length, seed):
        last_k = seed[0:self.order]
        output = last_k
        while len(output) < length:
            chars = self.model.get(last_k)
            choices = chars.keys()
            frequencies = [i/float(sum(chars.values())) for i in chars.values()]
            # print last_k, choices, frequencies
            output += random_pick(choices, frequencies)
            last_k = output[(len(output)-self.order):len(output)]
        return output


# make sure this works properly
def random_pick(char_list, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(char_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability: break
    return item


if __name__ == '__main__':
    t = TextGeneratorCharacter()
    t.read_file('output_short.txt') # TODO command line parameter
    t.train_model(10)
    t.save_model('markov_bot.json')
    for i in range(1,20):
      print t.generate_text(144, random.choice(string.letters))
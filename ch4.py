from tokenizer import tokenize, detokenize
import pprint
import os, random

class CircularBuffer(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.pointer = 0
        self.data = []

    def __len__(self):
        return len(self.data)

    def add(self, obj):
        if len(self.data) < self.capacity:
            self.data.append(obj)
        else:
            self.data[self.pointer] = obj
            self.pointer = (self.pointer + 1) % self.capacity

    def make_snapshot_tuple(self):
        return tuple(self.data[(self.pointer + i) % len(self.data)]
                     for i in range(len(self.data)))
        

class ConditionalCounts(object):
    def __init__(self):
        self.count = 0
        self.counts = {}

    def add_count(self, token):
        self.count += 1
        if token not in self.counts:
            self.counts[token] = 0
        self.counts[token] += 1

class Probability(object):
    def __init__(self, count, probability):
        self.count = count
        self.probability = probability

    def __str__(self):
        return "Count: {}, Probability: {:.04f}".format(
            self.count, self.probability)

    def __repr__(self):
        return str(self)

class ConditionalProbability(object):
    def __init__(self, count, condition_count):
        self.count = count
        self.condition_count = condition_count
        self.conditional_probability = count / condition_count

    def __str__(self):
        return (
            "Count: {}, Condition count: {}, Conditional prob: {}".format(
                self.count, self.condition_count,
                self.conditional_probability))

    def __repr__(self):
        return str(self)

class LanguageModel(object):
    def __init__(self, n):
        self.n = n
        # conditional_counts is a mapping from n-1 gram to ConditionalCounts.
        self.conditional_counts = {} if n > 1 else None
        # counts is a mapping from n-gram to count.
        self.counts = {}

    def add_n_gram(self, n_gram):
        if n_gram not in self.counts:
            self.counts[n_gram] = 0
        self.counts[n_gram] += 1
        if self.n > 1:
            n_1_gram = n_gram[:-1]
            if n_1_gram not in self.conditional_counts:
                self.conditional_counts[n_1_gram] = ConditionalCounts()
            self.conditional_counts[n_1_gram].add_count(n_gram[-1])

    def compute_probabilities(self):
        total_count = sum(v for k, v in self.counts.items())
        probs = [[k, Probability(v, v / total_count)]
                  for k, v in self.counts.items()]
        return sorted(probs, key=lambda x: -x[1].probability)

    def compute_conditional_probs(self):
        cond_probs = []
        for n_1_gram, cond_count in self.conditional_counts.items():
            for token, count in cond_count.counts.items():
                n_gram = n_1_gram + (token,)
                cond_probs.append(
                    [n_gram, ConditionalProbability(count, cond_count.count)])
        return sorted(cond_probs, key=lambda x: -x[1].conditional_probability)

    def _gen_random(self, count_map):
        """
        Given a count_map of token -> count, choose one randomly, 
        weighted by the count.
        """
        seq = [[k, v] for k, v in count_map.items()]
        cur_index = 0
        for elem in seq:
            count = elem[1]
            elem.extend([cur_index, cur_index + count])
            cur_index += count
        total_count = cur_index
        rand_index = random.randrange(total_count)
        return next(
            elem[0] for elem in seq if
            elem[2] <= rand_index and rand_index < elem[3])

    def _random_start_n_1_gram(self):
        count_map = { k: self.conditional_counts[k].count
                      for k in self.conditional_counts.keys()
                      if k[0] == '<s>' }
        return self._gen_random(count_map)

    def gen_random(self, token_length):
        cur_n_1_gram = self._random_start_n_1_gram()
        tokens = list(cur_n_1_gram)
        while len(tokens) < token_length:
            cond_count = self.conditional_counts[cur_n_1_gram]
            token = self._gen_random(cond_count.counts)
            tokens.append(token)
            n_gram = cur_n_1_gram + (token,)
            cur_n_1_gram = n_gram[1:]
        return tokens

def compute_n_gram_model(f, n, model=None, include_punctuation=False):
    """
    Returns a LanguageModel for text in file f.
    """
    if model is None:
        model = LanguageModel(n)
    circ_buff = CircularBuffer(n)
    circ_buff.add("<s>")
    for token in tokenize(f, include_punctuation=include_punctuation):
        circ_buff.add(token)
        if len(circ_buff) == n:
            model.add_n_gram(circ_buff.make_snapshot_tuple())
    return model

def compute_n_gram_model_for_dir(dir_name, n, include_punctuation=False):
    model = LanguageModel(n)
    for fn in os.listdir(dir_name):
        if fn == '.DS_Store':
            continue
        full_fn = os.path.join(dir_name, fn)
        with open(full_fn, 'r') as f:
            compute_n_gram_model(f, n, model, include_punctuation)
    return model

def ex_4_3():
    inaugural_uni_model = compute_n_gram_model_for_dir(
        '/Users/tony/Desktop/inaugural', 1)
    inaugural_bi_model = compute_n_gram_model_for_dir(
        '/Users/tony/Desktop/inaugural', 2)
    republic_uni_model = None
    republic_bi_model = None
    with open('/Users/tony/Desktop/platosrepublic.txt', 'r') as f:
        republic_uni_model = compute_n_gram_model(f, 1)
        f.seek(0)
        republic_bi_model = compute_n_gram_model(f, 2)
    republic_uni_probs = republic_uni_model.compute_probabilities()
    inaugural_uni_probs = inaugural_uni_model.compute_probabilities()
    print("Top unis from Republic:")
    pprint.pprint(republic_uni_probs[:100])
    print("Top unis from inaugural:")
    pprint.pprint(inaugural_uni_probs[:100])
    republic_bi_probs = republic_bi_model.compute_conditional_probs()
    inaugural_bi_probs = inaugural_bi_model.compute_conditional_probs()
    print("Top bis from Republic:")
    pprint.pprint(republic_bi_probs[:50])
    print("Top bis from Inaugural:")
    pprint.pprint(inaugural_bi_probs[:50])

def ex_4_4():
    inaugural_bi_model = compute_n_gram_model_for_dir(
        '/Users/tony/Desktop/inaugural', 3, True)
    random_tokens = inaugural_bi_model.gen_random(500)
    print(detokenize(random_tokens))

if __name__ == '__main__':
    ex_4_4()

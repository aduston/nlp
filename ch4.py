from tokenizer import tokenize

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

def compute_n_gram_model(f, n):
    """
    Returns a LanguageModel for text in file name fn.
    """
    model = LanguageModel(n)
    circ_buff = CircularBuffer(n)
    circ_buff.add("<s>")
    for token in tokenize(f):
        circ_buff.add(token)
        if len(circ_buff) == n:
            model.add_n_gram(circ_buff.make_snapshot_tuple())
    return model


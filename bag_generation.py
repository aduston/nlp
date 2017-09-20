class ViterbiCell(object):
    def __init__(self, n_1_gram, log_p, parent, used_words):
        """
        used_words is a set of words that have been used up to this path.
        """
        self.n_1_gram = n_1_gram
        self.log_p = log_p
        self.parent = parent
        self.used_words = used_words

def uniqueify(words):
    return ["{0}:{1}".format(i, w) for i, w in enumerate(words)]

def deuniqueify(words):
    return [(w.split(":", 2)[1] if ':' in w else w) for w in words]

def most_likely_sequence(word_bag, model, n):
    """
    word_bag is a list (i.e. multiset) of words
    model is a function which, given an n_gram (w_1, ..., w_n), returns log P(w_n|w_1...w_n-1)
    """
    last_words = [ViterbiCell(tuple("<s>" for i in range(n - 1)), 0.0, None, set())]
    word_bag = uniqueify(word_bag)
    for i in range(len(word_bag)):
        next_layer = {} # map of n-1 gram to ViterbiCell
        for word in word_bag:
            for last_word in last_words:
                if word not in last_word.used_words:
                    n_gram = last_word.n_1_gram + (word,)
                    n_1_gram = last_word.n_1_gram[1:] + (word,)
                    log_p = last_word.log_p + model(tuple(deuniqueify(n_gram)))
                    if n_1_gram not in next_layer or log_p > next_layer[n_1_gram].log_p:
                        next_layer[n_1_gram] = ViterbiCell(
                            n_1_gram, log_p, last_word, last_word.used_words | set(word))
        last_words = list(next_layer.values())
    ending_cell = max(last_words, key=lambda x: x.log_p)
    word_sequence = []
    cell = ending_cell
    while cell.parent is not None:
        word_sequence.append(cell.n_1_gram[-1])
        cell = cell.parent
    word_sequence.reverse()
    return deuniqueify(word_sequence)

from tokenizer import tokenize, detokenize
import pprint
import os, math, random

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

    def make_snapshot_tuple(self, n=None):
        return tuple(self.data[(self.pointer + i) % len(self.data)]
                     for i in range(len(self.data)))

class CountFrequency(object):
    def __init__(self, r, N_r):
        self.r = r
        self.N_r = N_r

    def __str__(self):
       return "r: {}, N_r: {}".format(self.r, self.N_r)

    def __repr__(self):
        return str(self)

def simple_linear_regression(count_frequencies):
    """
    log(N_r) = a + b * log(r)
    solve simple linear regression, return a and b
    using closed-form solution rather than gradient descent
        here since we don't have much data
    """
    X = [math.log(cf.r) for cf in count_frequencies]
    Y = [math.log(cf.N_r) for cf in count_frequencies]
    X_mean = sum(X) / len(X)
    Y_mean = sum(Y) / len(Y)
    b = sum((xy[0] - X_mean) * (xy[1] - Y_mean) for xy in zip(X, Y)) / \
        sum((x - X_mean) * (x - X_mean) for x in X)
    a = Y_mean - b * X_mean
    return a, b

def simple_good_turing_estimates(count_frequencies):
    """
    Returns a map of r -> p_r, where p_r is normalized.
    See Gale's explanation of Good-Turing for details: 
    https://pdfs.semanticscholar.org/3c0f/046634f8102c2acb495aaf7f14924c2d4ee7.pdf
    """
    N = sum(cf.r * cf.N_r for cf in count_frequencies)
    N_1 = next(cf for cf in count_frequencies if cf.r == 1).N_r
    a, b = simple_linear_regression(count_frequencies)
    smoother = SimpleGoodTuringCountSmoother(b)
    unnormalized_probs = {}
    for cf in count_frequencies:
        if cf.r not in unnormalized_probs:
            unnormalized_probs[cf.r] = smoother(cf.r) / N
    cf_map = { cf.r: cf.N_r for cf in count_frequencies }
    unnormalized_total = sum(cf_map[r] * p_r for r, p_r in unnormalized_probs.items())
    p_0 = N_1 / N
    nonzero_prob = (1.0 - p_0)
    normalized_probs = { 0: p_0 }
    for cf in count_frequencies:
        normalized_probs[cf.r] = \
            nonzero_prob * (unnormalized_probs[cf.r] / unnormalized_total)
    return normalized_probs

class SimpleGoodTuringCountSmoother(object):
    def __init__(self, b):
        self.b = b

    def __call__(self, r):
        return r * math.pow((1 + 1/r), self.b + 1)

class ConditionalCounts(object):
    def __init__(self):
        self.count = 0
        self.counts = {}

    def add_count(self, token):
        self.count += 1
        self.counts[token] = self.counts.get(token, 0) + 1

class Probability(object):
    def __init__(self, count, probability, sgt_smoothed_probability):
        self.count = count
        self.probability = probability
        self.sgt_smoothed_probability = sgt_smoothed_probability

    def __str__(self):
        return "Count: {}, Probability: {:.04f}, SGT-smoothed Probability: {:.04f}".format(
            self.count, self.probability, self.sgt_smoothed_probability)

    def __repr__(self):
        return str(self)

class ConditionalProbability(object):
    def __init__(self, count, condition_count, sgt_prob_n, sgt_prob_n_1):
        self.count = count
        self.condition_count = condition_count
        self.conditional_probability = count / condition_count
        self.sgt_conditional_probability = sgt_prob_n / sgt_prob_n_1

    def __str__(self):
        return (
            "Count: {}, Condition count: {}, Conditional prob: {}, SGT-smoothed conditional prob: {}".format(
                self.count,
                self.condition_count,
                self.conditional_probability,
                self.sgt_conditional_probability))

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
        self.counts[n_gram] = self.counts.get(n_gram, 0) + 1
        if self.n > 1:
            n_1_gram = n_gram[:-1]
            if n_1_gram not in self.conditional_counts:
                self.conditional_counts[n_1_gram] = ConditionalCounts()
            self.conditional_counts[n_1_gram].add_count(n_gram[-1])

    def compute_probabilities(self):
        total_count = sum(v for k, v in self.counts.items())
        sgt_estimates = simple_good_turing_estimates(
            self.n_gram_count_frequencies())
        probs = [[k, Probability(v, v / total_count, sgt_estimates[v])]
                  for k, v in self.counts.items()]
        return sorted(probs, key=lambda x: -x[1].probability)

    def compute_conditional_probs(self):
        n_sgt_estimates = simple_good_turing_estimates(
            self.n_gram_count_frequencies())
        n_1_sgt_estimates = simple_good_turing_estimates(
            self.n_1_gram_count_frequencies())
        cond_probs = []
        for n_1_gram, cond_count in self.conditional_counts.items():
            for token, count in cond_count.counts.items():
                n_gram = n_1_gram + (token,)
                cond_probs.append(
                    [n_gram, ConditionalProbability(
                        count,
                        cond_count.count,
                        n_sgt_estimates[count],
                        n_1_sgt_estimates[cond_count.count])])
        return sorted(cond_probs, key=lambda x: -x[1].conditional_probability)

    def n_1_gram_count_frequencies(self):
        gt_counts = {} # map of r to N_r
        for n_1_gram, cond_count in self.conditional_counts.items():
            gt_counts[cond_count.count] = gt_counts.get(cond_count.count, 0) + 1
        return [CountFrequency(r, N_r) for r, N_r in gt_counts.items()]

    def n_gram_count_frequencies(self):
        gt_counts = {} # map of r to N_r.
        for n_gram, count in self.counts.items():
            gt_counts[count] = gt_counts.get(count, 0) + 1
        return [CountFrequency(r, N_r) for r, N_r in gt_counts.items()]

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
    inaugural_n_model = compute_n_gram_model_for_dir(
        '/Users/tony/Desktop/inaugural', 3, True)
    random_tokens = inaugural_n_model.gen_random(500)
    print(detokenize(random_tokens))

def ex_4_4_b():
    republic_n_model = None
    with open('/Users/tony/Desktop/platosrepublic.txt', 'r') as f:
        republic_n_model = compute_n_gram_model(f, 3, include_punctuation=True)
    random_tokens = republic_n_model.gen_random(500)
    print(detokenize(random_tokens))

def illustrate_simple_good_turing_smoothing():
    inaugural_n_model = compute_n_gram_model_for_dir(
        '/Users/tony/Desktop/inaugural', 2, True)
    count_frequencies = inaugural_n_model.n_gram_count_frequencies()
    a, b = simple_linear_regression(count_frequencies)
    smoother = SimpleGoodTuringCountSmoother(b)
    for cf in count_frequencies:
        print("{0} {1} {2} {3}".format(
            cf.r, cf.N_r,
            smoother(cf.r),
            math.exp(a) * math.pow(cf.r, b)))

def ex_4_5():
    model = compute_n_gram_model_for_dir(
        '/Users/tony/Desktop/inaugural', 2)
    probs = model.compute_probabilities()
    pprint.pprint(probs[:10])
    cond_probs = model.compute_conditional_probs()
    pprint.pprint(cond_probs[:10])

if __name__ == '__main__':
    ex_4_5()

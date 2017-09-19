from ch4 import CircularBuffer, CountFrequency, \
    simple_linear_regression, SimpleGoodTuringCountSmoother
import math
from tokenizer import tokenize, detokenize
import pprint

class LanguageModel(object):
    def __init__(self, trie_node, N):
        self.trie_node = trie_node
        self.N = N

    def log_p_katz(self, n_gram):
        if n_gram[-1] not in self.trie_node.descendants:
            return math.log(self.trie_node.beta()) # degenerate case: w_n not in model
        node = self.trie_node.find_node(n_gram)
        if node is not None:
            return node.log_p_star()
        else:
            prefix = n_gram[:-1]
            prefix_node = self.trie_node.find_node(prefix)
            suffix = n_gram[1:]
            if prefix_node is None:
                return self.log_p_katz(suffix)
            else:
                return prefix_node.log_alpha + self.log_p_katz(suffix)

    def calc_perplexity(self, token_iterator):
        circ_buff = CircularBuffer(self.N)
        circ_buff.add("<s>")
        sum_log_p = 0.0
        token_count = 0
        for token in token_iterator:
            token_count += 1
            circ_buff.add(token)
            if len(circ_buff) == N: # skipping first N-1 tokens due to only an exercise.
                n_gram = circ_buff.make_snapshot_tuple()
                sum_log_p += self.log_p_katz(n_gram)
        return math.exp(-(1/token_count) * sum_log_p)

class KatzTrieNode(object):
    def __init__(self, n_gram=None, parent=None):
        if n_gram is None:
            self.n_gram = () # root trie node => empty tuple n-gram
        else:
            self.n_gram = n_gram
        self.parent = parent
        self.count = 0
        self.log_alpha = None
        self.discounter = None
        self.descendants = {}

    def populate(self, N_gram):
        self.count += 1
        if len(N_gram) > len(self.n_gram):
            suffix = N_gram[len(self.n_gram):]
            descendant = self.descendants.get(suffix[0], None)
            if descendant is None:
                descendant = self.descendants.setdefault(
                    suffix[0], KatzTrieNode(N_gram[:len(self.n_gram) + 1], self))
            descendant.populate(N_gram)

    def _is_start_prefix(self):
        return next((t for t in self.n_gram if t != '<s>'), None) is None

    def populate_count_frequencies(self, gt_counts, n):
        if n == len(self.n_gram) and not self._is_start_prefix():
            gt_counts[self.count] = gt_counts.get(self.count, 0) + 1
        else:
            for descendant in self.descendants.values():
                descendant.populate_count_frequencies(gt_counts, n)

    def set_discounter(self, discounter, n):
        if n == len(self.n_gram):
            self.discounter = discounter
        else:
            for descendant in self.descendants.values():
                descendant.set_discounter(discounter, n)

    def c_star(self):
        return self.discounter(self.count)

    def p_star(self):
        return self.c_star() / self.parent.count

    def log_p_star(self):
        return math.log(self.c_star()) - math.log(self.parent.count)

    def beta(self):
        return 1 - sum(d.p_star() for d in self.descendants.values())

    def find_node(self, n_gram):
        if len(n_gram) == 0:
            return self
        else:
            desc = self.descendants.get(n_gram[0], None)
            if desc is not None:
                return desc.find_node(n_gram[1:])
            else:
                return None

def _add_discounts(trie_node, N):
    for n in range(1, N + 1):
        gt_counts = {} # map of c to N_c
        trie_node.populate_count_frequencies(gt_counts, n)
        count_frequencies = [CountFrequency(r, N_r) for r, N_r in gt_counts.items()]
        a, b = simple_linear_regression(count_frequencies)
        trie_node.set_discounter(SimpleGoodTuringCountSmoother(b), n)

def _add_alphas(trie_node, N):
    stack = [trie_node]
    num_tokens = sum(tn.count for tn in stack)
    while len(stack) > 0:
        node = stack.pop()
        if len(node.n_gram) > 0:
            beta_n_1 = node.beta()
            suffix_node = trie_node.find_node(node.n_gram[1:])
            denominator = 1 - sum(d.p_star() for token, d
                                  in suffix_node.descendants.items()
                                  if token in node.descendants)
            node.log_alpha = math.log(beta_n_1) - math.log(denominator)
        for descendant in node.descendants.values():
            stack.append(descendant)

def populate_trie_nodes(f, N, include_punctuation=False, trie_node=None):
    if trie_node is None:
        trie_node = KatzTrieNode()
    circ_buff = CircularBuffer(N)
    for i in range(N - 1):
        circ_buff.add("<s>")
    n_gram = None
    for token in tokenize(f, include_punctuation=include_punctuation):
        circ_buff.add(token)
        if len(circ_buff) == N:
            n_gram = circ_buff.make_snapshot_tuple()
            trie_node.populate(n_gram)
    for i in range(1, len(n_gram)):
        trie_node.populate(n_gram[i:])
    return trie_node

def compute_trie_nodes_for_dir(dir_name, N, include_punctuation=False):
    trie_node = KatzTrieNode()
    for fn in os.listdir(dir_name):
        if fn == '.DS_Store':
            continue
        full_fn = os.path.join(dir_name, fn)
        with open(full_fn, 'r') as f:
            populate_trie_nodes(f, N, include_punctuation, trie_node)
    return trie_node

def compute_trie_nodes_for_file(fn, N, include_punctuation=False):
    with open(fn, 'r') as f:
        return populate_trie_nodes(f, N, include_punctuation)

def compute_model(trie_node, N):
    _add_discounts(trie_node, N)
    _add_alphas(trie_node, N)
    return trie_node

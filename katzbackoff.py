from ch4 import CircularBuffer, CountFrequency, \
    simple_linear_regression, SimpleGoodTuringCountSmoother
import math
from tokenizer import tokenize, detokenize
import pprint

class LanguageModel(object):
    def __init__(self, trie_nodes):
        self.trie_nodes = trie_nodes
        self.token_count = sum(tn.count for rn in trie_nodes.values())
        self.leftover_prob = \
            1 - sum(tn.c_star() for rn in trie_nodes.values()) / self.token_count

    def _find_node(self, n_gram):
        if n_gram[0] in self.trie_nodes:
            return self.trie_nodes[n_gram[0]].find_node(n_gram[1:])
        return None

    def p_katz(self, n_gram):
        if len(n_gram) == 1:
            if n_gram[0] in self.trie_nodes:
                return self.trie_nodes[n_gram[0]].c_star() / self.token_count
            else:
                return self.leftover_prob
        else:
            trie_node = self._find_node(n_gram[0])
            if trie_node is not None:
                return trie_node.p_star()
            else:
                prefix_node = self._find_node(n_gram[:-1])
                if prefix_node is not None:
                    return math.exp(prefix_node.log_alpha + \
                                    math.log(self.p_katz(n_gram[1:])))
                else:
                    return self.p_katz(n_gram[1:])

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

    def populate_count_frequencies(self, gt_counts, n):
        if n == len(self.n_gram):
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
        elif len(n_gram) == 1:
            return self.descendants[n_gram[0]]
        else:
            return self.descendants[n_gram[0]].find_node(n_gram[1:])

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

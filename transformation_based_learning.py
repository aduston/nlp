import itertools
from nltk.corpus import brown
from brown_tags import TAGS

class Template(object):
    def __init__(self, z_spec, w_spec=None):
        self.z_spec = z_spec if isinstance(z_spec, list) else [z_spec]
        self.w_spec = w_spec # always an int or None
        min_pos = min(self.z_spec)
        max_pos = max(self.z_spec)
        if w_spec is not None:
            min_pos = min(min_pos, w_spec)
            max_pos = max(max_pos, w_spec)
        self.min_pos = min_pos
        self.max_pos = max_pos

    def make_candidate(self, sentence, position):
        if position + self.min_pos < 0 or position + self.max_pos >= len(sentence):
            return None
        z_set, w_set = None, None
        z_set = set(sentence[position + offset][2]
                    for offset in range(self.z_spec[0], self.z_spec[-1] + 1))
        if self.w_spec is not None:
            w_set = set([sentence[position + self.w_spec][2]])
        return TemplateInstanceCandidate(z_set, w_set)

class TemplateInstanceCandidate(object):
    def __init__(self, z_set, w_set=None):
        self.z_set = z_set
        self.w_set = w_set
        self._key = "|".join(sorted(list(z_set)))
        if w_set is not None:
            self._key += "||"
            self._key += "|".join(sorted(list(w_set)))

    def __hash__(self):
        return self._key

    def __eq__(self, other):
        return self._key == other._key

    def __ne__(self, other):
        return not (self == other)

    def matches_args(self, z, w=None):
        if w is None:
            return z in self.z_set
        else:
            return (z in self.z_set) and (w in self.w_set)

class TemplateInstanceCandidates(object):
    def __init__(self, template):
        self.template = template
        # mappings of TemplateInstanceCandidate -> count
        self._good_candidates = {}
        self._bad_candidates = {}

    def _add_candidate(self, candidate, candidates):
        if candidate is None:
            return
        candidates[candidate] = \
            candidates.get(candidate, 0) + 1

    def add_good_candidate(self, candidate):
        self._add_candidate(candidate, self._good_candidates)

    def add_bad_candidate(self, candidate):
        self._add_candidate(candidate, self._bad_candidates)

    def get_best(self):
        args_iter = None
        if self.template.get_num_args() == 1:
            args_iter = ((t, None) for t in TAGS.keys())
        else:
            args_iter = itertools.product(TAGS.keys(), TAGS.keys())
        best_args, best_args_score = None, -sys.maxsize
        for z, w in args_iter:
            good_candidates_score = sum(
                v for k, v in self._good_candidates.items()
                if k.matches_args(z, w))
            bad_candidates_score = sum(
                v for k, v in self._bad_candidates.items()
                if k.matches_args(z, w))
            score = good_candidates_score - bad_candidates_score
            if score > best_args_score:
                best_args = (z, w)
                best_args_score = best_args_score
        return best_args[0], best_args[1], best_args_score

class TemplateInstance(object):
    def __init__(self, template, a, b, z, w=None):
        self.template = template
        self.a = a
        self.b = b
        self.z = z
        self.w = w

    def is_match(self, tag_sequence, position):
        if tag_sequence[position] != self.a:
            return False
        if position + self.template.min_pos < 0 or \
           position + self.template.max_pos >= len(tag_sequence):
            return False
        is_z_match = self.z in (tag_sequence[position + offset]
                                for offset in
                                range(self.template.z_spec[0],
                                      self.template.z_spec[-1] + 1))
        if self.template.w_spec is None:
            is_w_match = True
        else:
            is_w_match = self.w == tag_sequence[position + self.template.w_spec]
        return is_z_match and is_w_match

TEMPLATES = [ # same templates Brill used
    Template(-1),
    Template(-2),
    Template([-2, -1]),
    Template([1, 2]),
    Template([-3, -1]),
    Template([1, 3]),
    Template(-1, 1),
    Template(-1, -2),
    Template(-1, 2),
    Template(1, -2),
    Template(1, 2)
]

def tbl(corpus):
    """
    Returns a list of TemplateInstances
    """
    initialize_with_most_likely_tags(
        corpus, most_likely_tags.get_most_likely_tags(
            os.path.expanduser("~/most_likely_tags.txt")))
    transforms_queue = []
    for i in range(10): # we will just create a queue of 10 transforms
        best_transform = get_best_transform(corpus, TEMPLATES)
        apply_transform(best_transform, corpus)
        transforms_queue.append(best_transform)
    return transforms_queue

def initialize_with_most_likely_tags(corpus, most_likely_tags):
    for sentence in corpus.sentences():
        for tagged_word in sentence:
            tagged_word.append(most_likely_tags[tagged_word[0]])

def apply_transform(transform, corpus):
    for sentence in corpus.sentences():
        current_tags = [w[2] for w in sentence]
        for i in range(len(current_tags)):
            if transform.is_match(current_tags, i):
                sentence[i][2] = transform.b

def get_best_transform(corpus, templates):
    best_instance, best_score = None, -sys.maxsize
    for template in TEMPLATES:
        instance, score = get_best_instance(corpus, template)
        if score > best_score:
            best_instance = instance
            best_score = score
    return best_instance

def get_best_instance(corpus, template):
    """
    Returns a (template_instance, score) pair.
    """
    best_instance, best_instance_score = None, -sys.maxsize
    for from_tag, to_tag in itertools.product(TAGS.keys(), TAGS.keys()):
        if from_tag == to_tag:
            continue
        candidates = TemplateInstanceCandidates(template)
        for sentence in corpus.sentences():
            for i in range(len(sentence)):
                 
                if sentence[i][2] == from_tag:
                    if sentence[i][1] == to_tag:
                        candidates.add_good_candidate(
                            template.make_candidate(sentence, i))
                    elif sentence[i][1] == from_tag:
                        candidates.add_bad_candidate(
                            template.make_candidate(sentence, i))
        z, w, score = candidates.get_best()
        if score > best_instance_score:
            best_instance_score = score
            best_instance = TemplateInstance(
                template, from_tag, to_tag, z, w)
    return best_instance, best_instance_score

import os, sys, itertools, logging
import most_likely_tags as mlt
from nltk.corpus import brown
from brown_tags import TAGS

log = logging.getLogger("tbl")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(ch)

class Corpus(object):
    def __init__(self, sentences):
        self._sentences = [[TaggedWord(w, t) for w, t in sent] for sent in sentences]

    def sentences(self):
        return self._sentences

    @staticmethod
    def from_brown_tagged_corpus(categories):
        brown_sents = brown.tagged_sents(categories=categories)
        simplified_tag_sents = []
        for sent in brown_sents:
            simplified = []
            for w, t in sent:
                if t != "--":
                    t = t.split("-", maxsplit=1)[0]
                    t = t.split("+", maxsplit=1)[0]
                if t != "*" and t.endswith("*"):
                    t = t[:-1]
                simplified.append((w, t))
            simplified_tag_sents.append(simplified)
        return Corpus(simplified_tag_sents)

    def __len__(self):
        return sum(len(s) for s in self._sentences)

    def num_right(self):
        return sum(sum(1 if w.current_tag == w.correct_tag else 0
                       for w in s) for s in self._sentences)

class TaggedWord(object):
    def __init__(self, word, correct_tag):
        self.word = word
        self.correct_tag = correct_tag
        self.current_tag = None

    def __str__(self):
        return "{}: {}/{}".format(self.word, self.correct_tag, self.current_tag)

    def __repr__(self):
        return str(self)

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

    def __str__(self):
        if len(self.z_spec) == 1 and self.w_spec is None:
            return "Change a to b when token in position {} is z".format(self.z_spec[0])
        elif len(self.z_spec) > 1:
            return "Change a to b when any token in positions {} to {} is z".format(
                self.z_spec[0], self.z_spec[-1])
        else:
            return ("Change a to b when token in position {} is z "
                    "and token in position {} is w").format(
                        self.z_spec[0], self.w_spec[0])

    def __repr__(self):
        return str(self)

    def get_num_args(self):
        return 1 if self.w_spec is None else 2

    def make_candidate(self, sentence, position):
        if position + self.min_pos < 0 or position + self.max_pos >= len(sentence):
            return None
        z_set, w_set = None, None
        z_set = set(sentence[position + offset].current_tag
                    for offset in range(self.z_spec[0], self.z_spec[-1] + 1))
        if self.w_spec is not None:
            w_set = set([sentence[position + self.w_spec].current_tag])
        return TemplateInstanceCandidate(z_set, w_set)

class TemplateInstanceCandidate(object):
    def __init__(self, z_set, w_set=None):
        self.z_set = z_set
        self.w_set = w_set
        self._z_value = None if len(z_set) == 0 else list(z_set)[0]
        self._w_value = None if w_set is None or len(w_set) == 0 else list(w_set)[0]
        self._key = "|".join(sorted(list(z_set)))
        if w_set is not None:
            self._key += "||"
            self._key += "|".join(sorted(list(w_set)))
        self._hash = hash(self._key)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return self._hash == other._hash

    def __ne__(self, other):
        return not (self == other)

    def z_w_pair(self):
        if self._z_value is None or self._w_value is None:
            raise Exception()
        return (self._z_value, self._w_value)

    def matches_args(self, z, w=None):
        if w is None:
            return z in self.z_set
        else:
            if self._z_value is not None and self._w_value is not None:
                return z == self._z_value and w == self._w_value
            else:
                return z in self.z_set and w in self.w_set

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
        candidates = set(list(self._good_candidates.keys()) +
                         list(self._bad_candidates.keys()))
        if self.template.get_num_args() == 1:
            possible_z_tags = set().union(*[c.z_set for c in candidates])
            args_iter = ((t, None) for t in possible_z_tags)
        else:
            args_iter = [c.z_w_pair() for c in candidates]
        best_args, best_args_score = ('NN', 'NN'), -sys.maxsize
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
                best_args_score = score
        return best_args[0], best_args[1], best_args_score

class TemplateInstance(object):
    def __init__(self, template, a, b, z, w=None):
        self.template = template
        self.a = a
        self.b = b
        self.z = z
        self.w = w

    def __str__(self):
        if len(self.template.z_spec) == 1 and self.template.w_spec is None:
            return "Change {} to {} when token in position {} is {}".format(
                self.a, self.b, self.template.z_spec[0], self.z)
        elif len(self.template.z_spec) > 1:
            return "Change {} to {} when any token in positions {} to {} is {}"\
                .format(self.a, self.b, self.template.z_spec[0],
                        self.template.z_spec[-1], self.z)
        else:
            return ("Change {} to {} to when token in position {} "
                    "is {} and token in position {} is {}").format(
                        self.a, self.b, self.template.z_spec[0], self.z,
                        self.template.w_spec[0], self.w)

    def __repr__(self):
        return str(self)

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
        corpus, mlt.get_most_likely_tags(
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
            tagged_word.current_tag = most_likely_tags[tagged_word.word]

def apply_transform(transform, corpus):
    for sentence in corpus.sentences():
        current_tags = [w.current_tag for w in sentence]
        for i in range(len(current_tags)):
            if transform.is_match(current_tags, i):
                sentence[i].current_tag = transform.b

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
    log.debug("Getting best instance for template '%s'", template)
    best_instance, best_instance_score = None, -sys.maxsize
    pair_count = 0
    for from_tag, to_tag in itertools.product(TAGS.keys(), TAGS.keys()):
        if from_tag == to_tag:
            continue
        pair_count += 1
        if pair_count % 1000 == 0:
            log.debug("At pair count %d", pair_count)
        candidates = TemplateInstanceCandidates(template)
        for sentence in corpus.sentences():
            for i in range(len(sentence)):
                w = sentence[i]
                if w.current_tag == from_tag:
                    if w.correct_tag == to_tag:
                        candidates.add_good_candidate(
                            template.make_candidate(sentence, i))
                    elif w.correct_tag == from_tag:
                        candidates.add_bad_candidate(
                            template.make_candidate(sentence, i))
        z, w, score = candidates.get_best()
        if score > best_instance_score:
            best_instance_score = score
            best_instance = TemplateInstance(
                template, from_tag, to_tag, z, w)
    log.debug("Determined best instance for template: %s", best_instance)
    return best_instance, best_instance_score

if __name__ == '__main__':
    corpus = Corpus.from_brown_tagged_corpus("news")
    transforms_queue = tbl(corpus)
    print("Obtained transformation queue, according to the brown news corpus:")
    for t in transforms_queue:
        print(t)

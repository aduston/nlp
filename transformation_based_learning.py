import itertools
from brown_tags import TAGS

class Template(object):
    def __init__(self, z_spec, w_spec=None):
        self.z_spec = z_spec
        self.w_spec = w_spec

    def make_candidate(self, corpus, position):
        pass # TODO: left off here

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

    def add_good_candidate(self, candidate):
        if candidate is None:
            return
        self._good_candidates[candidate] = \
            self._good_candidates.get(candidate, 0) + 1

    def add_bad_candidate(self, candidate):
        if candidate is None:
            return
        self._bad_candidates[candidate] = \
            self._bad_candidates.get(candidate, 0) + 1

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
    def __init__(self, a, b, z, w=None):
        self.a = a
        self.b = b
        self.z = z
        self.w = w

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

def get_best_instance(corpus, template):
    """
    Returns a (template_instance, score) pair.
    """
    best_instance, best_instance_score = None, -sys.maxsize
    for from_tag, to_tag in itertools.product(TAGS.keys(), TAGS.keys()):
        candidates = TemplateInstanceCandidates(template)
        for i in range(corpus.size()):
            if corpus.current_tag(i) == from_tag:
                if corpus.correct_tag(i) == to_tag:
                    candidates.add_good_candidate(
                        template.make_candidate(corpus, i))
                elif corpus.correct_tag(i) == from_tag:
                    candidates.add_bad_candidate(
                        template.make_candidate(corpus, i))
        z, w, score = candidates.get_best()
        if score > best_instance_score:
            best_instance_score = score
            best_instance = TemplateInstance(
                from_tag, to_tag, z, w)
    return best_instance, best_instance_score

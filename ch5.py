import sys, os, string, math
from collections import namedtuple
import most_likely_tags, brown_tags
from transformation_based_learning import Corpus

def ch5_6():
    mlt = most_likely_tags.get_most_likely_tags(
        os.path.expanduser("~/most_likely_tags.txt"))
    corpus = Corpus.from_brown_tagged_corpus(categories='fiction')
    for s in corpus.sentences():
        for w in s:
            w.current_tag = mlt.get(w.word, "NN")
    print("Using most likely tags with unknown always 'NN', we have {} right out of {}.".format(
        corpus.num_right(), len(corpus)))
    for s in corpus.sentences():
        first_word = True
        for w in s:
            if w.word not in mlt:
                if not first_word and w.word[0] in string.ascii_uppercase:
                    w.current_tag = "NP"
                elif w.word.endswith("s"):
                    w.current_tag = "NNS"
                elif w.word.endswith("ed"):
                    w.current_tag = "VBN"
                elif w.word.endswith("able"):
                    w.current_tag = "JJ"
                elif "-" in w.word:
                    w.current_tag = "JJ"
            first_word = False
    print("Using five naive rules for unknown words, we have {} right out of {}.".format(
        corpus.num_right(), len(corpus)))

def _convert_counts_to_log_conditional(counts):
    log_conditionals = {}
    for condition in counts.keys():
        conditional_counts = counts[condition]
        condition_count = sum(c for outcome, c in conditional_counts.items())
        log_prob_dict = {}
        for outcome, c in conditional_counts.items():
            log_prob_dict[outcome] = math.log(c) - math.log(condition_count)
        log_conditionals[condition] = log_prob_dict
    return log_conditionals
    
def _make_transition_probs(corpus):
    """
    Returns { tag_0 -> { tag_1: count }. Sentence start represented with special tag <n>.
    """
    probs = {}
    for s in corpus.sentences():
        prev_tag = "<s>"
        for w in s:
            if prev_tag not in probs:
                probs[prev_tag] = {}
            tag_0_dict = probs[prev_tag]
            tag_0_dict[w.correct_tag] = tag_0_dict.get(w.correct_tag, 0) + 1
            prev_tag = w.correct_tag
    return _convert_counts_to_log_conditional(probs)

def _make_conditional_probs(corpus):
    """
    Returns { tag -> { word: count }}
    """
    probs = {}
    for s in corpus.sentences():
        for w in s:
            if w.correct_tag not in probs:
                probs[w.correct_tag] = {}
            tag_dict = probs[w.correct_tag]
            tag_dict[w.word] = tag_dict.get(w.word, 0) + 1
    return _convert_counts_to_log_conditional(probs)

def most_likely_tag_sequence(words, transition_probs, conditional_probs):
    tags = list(brown_tags.TAGS.keys())
    ViterbiCell = namedtuple("ViterbiCell", ['tag', 'log_prob', 'prev_cell'])
    prev_row = [ViterbiCell("<s>", 0.0, None)]
    for w in words:
        cur_row = []
        for tag in tags:
            conditional_prob = conditional_probs[tag].get(w, -sys.maxsize)
            max_prev_cell, max_log_prob = None, -sys.maxsize
            for cell in prev_row:
                log_prob = cell.log_prob + \
                           transition_probs[cell.tag].get(tag, -sys.maxsize)
                if log_prob > max_log_prob:
                    max_prev_cell, max_log_prob = cell, log_prob
            cur_row.append(
                ViterbiCell(tag, conditional_prob + max_log_prob,
                            max_prev_cell))
        prev_row = cur_row
    max_cell = max((c for c in prev_row), key=lambda x: x.log_prob)
    path = []
    cell = max_cell
    while not cell is None:
        path.append(cell.tag)
        cell = cell.prev_cell
    return [c.tag for c in path.reverse()]

def ch5_8():
    corpus = Corpus.from_brown_tagged_corpus('news')
    transition_probs = _make_transition_probs(corpus)
    conditional_probs = _make_conditional_probs(corpus)
    fiction_corpus = Corpus.from_brown_tagged_corpus('fiction')
    for s in fiction_corpus.sentences():
        words = [w.word for w in s]
        tags = most_likely_tag_sequence(words, transition_probs, conditional_probs)
        print([w.correct_tag for w in s])
        print(tags)
        return

if __name__ == '__main__':
    ch5_8()

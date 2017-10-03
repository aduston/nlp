import sys, os, string, math
from collections import namedtuple
import most_likely_tags, brown_tags
from transformation_based_learning import Corpus

def unknown_word_tag(mlt, word, first_word=False):
    if word in mlt:
        return mlt[word]
    else:
        if not first_word and word[0] in string.ascii_uppercase:
            return "NP"
        elif word.endswith("s"):
            return "NNS"
        elif word.endswith("ed"):
            return "VBN"
        elif word.endswith("able"):
            return "JJ"
        elif "-" in word:
            return "JJ"
        else:
            return "NN"

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
            w.current_tag = unknown_word_tag(mlt, w.word[0], first_word)
            first_word = False
    print("Using five naive rules for unknown words, we have {} right out of {}.".format(
        corpus.num_right(), len(corpus)))

def convert_counts_to_log_conditional(counts):
    log_conditionals = {}
    for condition in counts.keys():
        conditional_counts = counts[condition]
        condition_count = sum(c for outcome, c in conditional_counts.items())
        log_prob_dict = {}
        for outcome, c in conditional_counts.items():
            log_prob_dict[outcome] = math.log(c) - math.log(condition_count)
        log_conditionals[condition] = log_prob_dict
    return log_conditionals
    
def add_transition_counts(corpus, counts):
    """
    counts in format { tag_0 -> { tag_1: count }. Sentence start represented with special tag <n>.
    """
    for s in corpus.sentences():
        prev_tag = "<s>"
        for w in s:
            if prev_tag not in counts:
                counts[prev_tag] = {}
            tag_0_dict = counts[prev_tag]
            tag_0_dict[w.correct_tag] = tag_0_dict.get(w.correct_tag, 0) + 1
            prev_tag = w.correct_tag
    return counts

def add_conditional_counts(corpus, counts):
    """
    counts in format { tag -> { word: count }}
    """
    for s in corpus.sentences():
        for w in s:
            if w.correct_tag not in counts:
                counts[w.correct_tag] = {}
            tag_dict = counts[w.correct_tag]
            tag_dict[w.word] = tag_dict.get(w.word, 0) + 1
    return counts

def most_likely_tag_sequence(words, transition_probs, conditional_probs, mlt=None):
    tags = list(conditional_probs.keys())
    ViterbiCell = namedtuple("ViterbiCell", ['tag', 'log_prob', 'prev_cell'])
    prev_row = [ViterbiCell("<s>", 0.0, None)]
    first_word = True
    for w in words:
        cur_row = []
        for tag in tags:
            conditional_prob = conditional_probs[tag].get(w, None)
            if conditional_prob is None and mlt is not None:
                unknown_tag = unknown_word_tag(mlt, w, first_word)
                if unknown_tag == tag:
                    conditional_prob = 0.0
            max_prev_cell, max_log_prob = None, -sys.maxsize
            for cell in prev_row:
                log_transition_prob = None
                if cell.tag in transition_probs:
                    log_transition_prob = transition_probs[cell.tag].get(
                        tag, None)
                if log_transition_prob is not None:
                    log_prob = cell.log_prob + log_transition_prob
                else:
                    log_prob = None
                if log_prob is not None and log_prob > max_log_prob:
                    max_prev_cell, max_log_prob = cell, log_prob
            if conditional_prob is not None and max_log_prob is not None:
                cur_row.append(
                    ViterbiCell(tag, conditional_prob + max_log_prob,
                                max_prev_cell))
        prev_row = cur_row
        first_word = False
    max_cell = max((c for c in prev_row), key=lambda x: x.log_prob)
    path = []
    cell = max_cell
    while cell is not None:
        if cell.tag != "<s>":
            path.append(cell.tag)
        cell = cell.prev_cell
    return list(reversed(path))

def ch5_8():
    transition_counts, conditional_counts = {}, {}
    corpus = Corpus.from_brown_tagged_corpus('news')
    add_transition_counts(corpus, transition_counts)
    add_conditional_counts(corpus, conditional_counts)
    corpus = Corpus.from_brown_tagged_corpus('romance')
    add_transition_counts(corpus, transition_counts)
    add_conditional_counts(corpus, conditional_counts)
    transition_probs = convert_counts_to_log_conditional(transition_counts)
    conditional_probs = convert_counts_to_log_conditional(conditional_counts)
    corpus = Corpus.from_brown_tagged_corpus('mystery')
    mlt = most_likely_tags.get_most_likely_tags(
        os.path.expanduser("~/most_likely_tags.txt"))
    accuracies = []
    for s in corpus.sentences():
        words = [w.word for w in s]
        tags = most_likely_tag_sequence(words, transition_probs, conditional_probs, mlt)
        combined_tags = list(zip([w.correct_tag for w in s], tags))
        accuracy = len(list(c for c in combined_tags if c[0] == c[1])) / len(combined_tags)
        accuracies.append(accuracy)
        if len(accuracies) % 1000 == 0:
            print("At sentence {}".format(len(accuracies)))
    # The following line will print that I have a total accuracy of 0.87, which is
    # about 0.09 lower than real taggers
    print("Total accuracy: {}".format(sum(accuracies) / len(accuracies)))

if __name__ == '__main__':
    ch5_8()

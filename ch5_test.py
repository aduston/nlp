import unittest
import math
import ch5
import transformation_based_learning as tbl

SENTENCES = [
    [['The', 'AT'], ['victory', 'NN'], ['was', 'BEDZ'], ['the', 'NN'],
     ['first', 'OD'], ['of', 'IN'], ['the', 'AT'], ['season', 'NN'],
     ['for', 'IN'], ['the', 'AT'], ['Billikens', 'NPS'], ['after', 'IN'],
     ['nine', 'CD'], ['defeats', 'NNS'], ['and', 'CC'], ['a', 'AT'],
     ['tie', 'NN'], ['.', '.']],
    [['The', 'AT'], ['tie', 'NN'], ['was', 'BEDZ'], ['against', 'IN'],
     ['Southeast', 'JJ-TL'], ['Missouri', 'NP-TL'], ['last', 'AP'],
     ['Friday', 'NR'], ['.', '.']]
]

class HMMTrainingTests(unittest.TestCase):
    def test_transition_counts(self):
        corpus = tbl.Corpus(SENTENCES)
        transition_counts = {}
        ch5.add_transition_counts(corpus, transition_counts)
        self.assertEqual({ "AT": 2 }, transition_counts['<s>'])
        self.assertEqual({ "NPS": 1, "NN": 4 }, transition_counts['AT'])

    def test_conditional_counts(self):
        corpus = tbl.Corpus(SENTENCES)
        conditional_counts = {}
        ch5.add_conditional_counts(corpus, conditional_counts)
        self.assertEqual({'a': 1, 'the': 2, 'The': 2}, conditional_counts['AT'])

    def test_convert_to_log_conditional(self):
        corpus = tbl.Corpus(SENTENCES)
        conditional_counts = {}
        ch5.add_conditional_counts(corpus, conditional_counts)
        log_conditionals = ch5.convert_counts_to_log_conditional(conditional_counts)
        self.assertEqual(
            { 'a': math.log(0.2), 'the': math.log(0.4), 'The': math.log(0.4) },
            log_conditionals['AT'])

class HMMPredictionTests(unittest.TestCase):
    def test_prediction(self):
        corpus = tbl.Corpus(SENTENCES)
        t_counts, c_counts = {}, {}
        ch5.add_transition_counts(corpus, t_counts)
        ch5.add_conditional_counts(corpus, c_counts)
        t_probs = ch5.convert_counts_to_log_conditional(t_counts)
        c_probs = ch5.convert_counts_to_log_conditional(c_counts)
        words = [w[0] for w in SENTENCES[0]]
        tags = ch5.most_likely_tag_sequence(words, t_probs, c_probs)
        self.assertEqual(
            ['<s>', 'AT', 'NN', 'BEDZ', 'NN', 'OD', 'IN', 'AT', 'NN', 'IN',
             'AT', 'NPS', 'IN', 'CD', 'NNS', 'CC', 'AT', 'NN', '.'],
            tags)

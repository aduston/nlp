import unittest, tempfile, os
import most_likely_tags as mlt
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

class InitializeTests(unittest.TestCase):
    def test_initialize(self):
        corpus = tbl.Corpus(SENTENCES)
        most_likely_tags = None
        f, fn = tempfile.mkstemp()
        os.close(f)
        try:
            mlt.save_most_likely_tags(corpus, fn)
            most_likely_tags = mlt.get_most_likely_tags(fn)
        finally:
            os.unlink(fn)
        tbl.initialize_with_most_likely_tags(corpus, most_likely_tags)
        current_the_tags = set()
        for s in corpus.sentences():
            current_the_tags |= set(w.current_tag for w in s if w.word == 'the')
        self.assertEqual(['AT'], list(current_the_tags))

class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.t0 = tbl.Template(-1)
        self.t1 = tbl.Template([1, 3])
        self.t2 = tbl.Template(-1, 1)
        self.corpus = tbl.Corpus(SENTENCES)
        for s in self.corpus.sentences():
            for w in s:
                if w.word == 'the':
                    w.current_tag = 'AT'
                else:
                    w.current_tag = w.correct_tag
    
    def test_make_candidate(self):
        sentence = next(s for s in self.corpus.sentences())
        self.assertEqual(None, self.t0.make_candidate(sentence, 0))
        candidate = self.t0.make_candidate(sentence, 1)
        self.assertEqual(["AT"], list(candidate.z_set))
        self.assertEqual(None, candidate.w_set)
        self.assertEqual(None, self.t1.make_candidate(sentence, 16))
        candidate = self.t1.make_candidate(sentence, 14)
        self.assertEqual([".", "AT", "NN"], sorted(list(candidate.z_set)))
        self.assertEqual(None, candidate.w_set)
        self.assertEqual(None, self.t2.make_candidate(sentence, 0))
        self.assertEqual(None, self.t2.make_candidate(sentence, 17))
        candidate = self.t2.make_candidate(sentence, 14)
        self.assertEqual(["NNS"], list(candidate.z_set))
        self.assertEqual(["AT"], list(candidate.w_set))

class GetBestInstanceTests(unittest.TestCase):
    def setUp(self):
        self.corpus = tbl.Corpus(SENTENCES)
        for s in self.corpus.sentences():
            for w in s:
                if w.word == 'the':
                    w.current_tag = 'AT'
                else:
                    w.current_tag = w.correct_tag

    def test_single_simple_arg(self):
        t0 = tbl.Template(-1)
        best_instance, best_instance_score = \
            tbl.get_best_instance(self.corpus, t0)
        self.assertEqual("AT", best_instance.a)
        self.assertEqual("NN", best_instance.b)
        self.assertEqual("BEDZ", best_instance.z)
        self.assertEqual(None, best_instance.w)

    def test_single_range_arg(self):
        t0 = tbl.Template([1, 3])
        best_instance, best_instance_score = \
            tbl.get_best_instance(self.corpus, t0)
        self.assertEqual("AT", best_instance.a)
        self.assertEqual("NN", best_instance.b)
        self.assertTrue(best_instance.z in ["OD", "IN", "AT"])
        self.assertEqual(None, best_instance.w)

    def test_double_arg(self):
        t0 = tbl.Template(-1, 1)
        best_instance, best_instance_score = \
            tbl.get_best_instance(self.corpus, t0)
        self.assertEqual("AT", best_instance.a)
        self.assertEqual("NN", best_instance.b)
        self.assertEqual("BEDZ", best_instance.z)
        self.assertEqual("OD", best_instance.w)

class TblTests(unittest.TestCase):
    def setUp(self):
        self.corpus = tbl.Corpus(SENTENCES)
        for s in self.corpus.sentences():
            for w in s:
                if w.word == 'the':
                    w.current_tag = 'AT'
                else:
                    w.current_tag = w.correct_tag

    def test_apply_transform(self):
        t0 = tbl.Template(-1)
        best_instance, best_instance_score = \
            tbl.get_best_instance(self.corpus, t0)
        tbl.apply_transform(best_instance, self.corpus)
        self.assertEqual("NN", self.corpus.sentences()[0][3].current_tag)

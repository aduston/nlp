import unittest
import io, math
import ch4

class CircularBufferTests(unittest.TestCase):
    def test_tuple(self):
        c = ch4.CircularBuffer(4)
        c.add("a")
        c.add("b")
        tup = c.make_snapshot_tuple()
        self.assertEqual(tup, ("a", "b"))
        c.add("c")
        c.add("d")
        c.add("e")
        self.assertEqual(
            c.make_snapshot_tuple(),
            ("b", "c", "d", "e"))

class LanguageModelTests(unittest.TestCase):
    def test_unigrams(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        model = ch4.compute_n_gram_model(f, 1)
        probs = model.compute_probabilities()
        self.assertEqual(('humpty',), probs[0][0])
        self.assertEqual(3, probs[0][1].count)

    def test_bigrams(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        model = ch4.compute_n_gram_model(f, 2)
        probs = model.compute_probabilities()
        humpty_dumpty = next(p for p in probs if p[0] == ('humpty', 'dumpty',))
        self.assertEqual(2, humpty_dumpty[1].count)
        cond_probs = model.compute_conditional_probs()
        humpty = [p for p in cond_probs if p[0][0] == 'humpty']
        self.assertEqual(2, len(humpty))
        humpty_dumpty = next(h for h in humpty if h[0] == ('humpty', 'dumpty',))
        humpty_together = next(h for h in humpty if h[0] == ('humpty', 'together'))
        self.assertAlmostEqual(
            humpty_dumpty[1].conditional_probability, 0.66667, places=3)
        self.assertAlmostEqual(
            humpty_together[1].conditional_probability, 0.33333, places=3)

    def test_n_gram_count_frequencies(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        model = ch4.compute_n_gram_model(f, 2)
        cfs = model.n_gram_count_frequencies()
        cfs = sorted(cfs, key=lambda cf: cf.r)
        self.assertEqual(1, cfs[0].r)
        self.assertEqual(21, cfs[0].N_r)
        self.assertEqual(2, cfs[1].r)
        self.assertEqual(4, cfs[1].N_r)

    def test_simple_linear_regression(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        model = ch4.compute_n_gram_model(f, 2)
        cfs = model.n_gram_count_frequencies()
        a, b = ch4.simple_linear_regression(cfs)
        self.assertAlmostEqual(21, math.exp(a + b * math.log(1)), places=3)
        self.assertAlmostEqual(4, math.exp(a + b * math.log(2)), places=3)

    def test_simple_good_turing_probs(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        model = ch4.compute_n_gram_model(f, 2)
        probs = model.compute_probabilities()
        prob = probs[0][1]
        self.assertAlmostEqual(0.0690, prob.probability, places=4)
        self.assertAlmostEqual(0.0250, prob.sgt_smoothed_probability, places=4)

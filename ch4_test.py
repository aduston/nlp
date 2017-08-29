import unittest
import io
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

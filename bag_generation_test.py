import io, sys, random, math
import unittest
import ch4, bag_generation, tokenizer

class BagGenerationTests(unittest.TestCase):
    def test_bigram_model(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        word_bag = list(tokenizer.tokenize(f))
        random.shuffle(word_bag)
        f.seek(0)
        model = ch4.compute_n_gram_model(f, 2)
        cond_probs = dict(model.compute_conditional_probs())
        def cond_prob(bigram):
            if bigram in cond_probs:
                return math.log(cond_probs[bigram].conditional_probability)
            else:
                return -sys.maxsize - 1
        seq = bag_generation.most_likely_sequence(word_bag, cond_prob, 2)
        self.assertEqual(["humpty", "dumpty"], seq[:2])

    def test_trigram_model(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        word_bag = list(tokenizer.tokenize(f))
        random.shuffle(word_bag)
        f.seek(0)
        model = ch4.compute_n_gram_model(f, 3)
        cond_probs = dict(model.compute_conditional_probs())
        def cond_prob(trigram):
            if trigram in cond_probs:
                return math.log(cond_probs[trigram].conditional_probability)
            else:
                return -sys.maxsize - 1
        seq = bag_generation.most_likely_sequence(word_bag, cond_prob, 3)
        self.assertEqual(
            ['humpty', 'dumpty', 'sat', 'on', 'a', 'wall', 'humpty',
             'dumpty', 'had', 'a', 'great', 'fall', 'all', 'the', 'king',
             "'s", 'horses', 'and', 'all', 'the', 'king', "'s", 'men',
             'could', 'not', 'put', 'humpty', 'together', 'again'],
            seq)

import ch4, katzbackoff
import unittest
import io, math

class LanguageModelTests(unittest.TestCase):
    def test_trie_nodes(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        trie_node = katzbackoff.populate_trie_nodes(f, 3, False)
        self.assertEqual(30, trie_node.count)
        humpty_node = trie_node.descendants['humpty']
        self.assertEqual(3, humpty_node.count)
        self.assertEqual(('humpty',), humpty_node.n_gram)
        self.assertEqual(2, len(humpty_node.descendants))
        dumpty_node = humpty_node.descendants['dumpty']
        together_node = humpty_node.descendants['together']
        self.assertEqual(2, dumpty_node.count)
        self.assertEqual(('humpty', 'dumpty',), dumpty_node.n_gram)
        self.assertEqual(1, together_node.count)
        self.assertEqual(2, len(dumpty_node.descendants))
        sat_node = dumpty_node.descendants['sat']
        self.assertEqual(1, sat_node.count)
        self.assertEqual(('humpty', 'dumpty', 'sat',), sat_node.n_gram)
        self.assertEqual(0, len(sat_node.descendants))
        self.assertEqual(1, len(together_node.descendants))
        self.assertEqual(0, len(together_node.descendants['again'].descendants))

    def test_trie_nodes_terminal(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        trie_node = katzbackoff.populate_trie_nodes(f, 3, False)
        self.assertTrue('together' in trie_node.descendants)

    def _n_gram_nodes(self, trie_node, n):
        nodes = {}
        stack = [trie_node]
        while len(stack) > 0:
            node = stack.pop()
            if len(node.n_gram) == n:
                nodes[node.n_gram] = node
            elif len(node.n_gram) < n:
                for d in node.descendants.values():
                    stack.append(d)
        return nodes

    def test_c_star_bigrams(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        trie_node = katzbackoff.compute_model(katzbackoff.populate_trie_nodes(f, 3), 3)
        bigram_nodes = self._n_gram_nodes(trie_node, 2)
        # idea here is to compare discounted counts to those obtained
        # through other method
        f.seek(0)
        cfs = ch4.compute_n_gram_model(f, 2).n_gram_count_frequencies()
        a, b = ch4.simple_linear_regression(cfs)
        discount = ch4.SimpleGoodTuringCountSmoother(b)
        for node in bigram_nodes.values():
            self.assertEqual(discount(node.count), node.c_star())

    def test_c_star_trigrams(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        trie_node = katzbackoff.compute_model(katzbackoff.populate_trie_nodes(f, 3), 3)
        trigram_nodes = self._n_gram_nodes(trie_node, 3)
        # idea here is to compare discounted counts to those obtained
        # through other method
        f.seek(0)
        cfs = ch4.compute_n_gram_model(f, 3).n_gram_count_frequencies()
        a, b = ch4.simple_linear_regression(cfs)
        discount = ch4.SimpleGoodTuringCountSmoother(b)
        for node in trigram_nodes.values():
            self.assertEqual(discount(node.count), node.c_star())

    def test_alpha(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Dumpty together again.") # note we changed Humpty -> Dumpty
        trie_node = katzbackoff.compute_model(katzbackoff.populate_trie_nodes(f, 3), 3)
        humpty_node = trie_node.descendants['humpty']
        humpty_dumpty_node = humpty_node.descendants['dumpty']
        dumpty_node = trie_node.descendants['dumpty']
        # alpha(humpty dumpty)
        beta_n_1 = 1.0 - sum(d.p_star() for d in humpty_dumpty_node.descendants.values())
        denominator = 1.0 - sum(d.p_star() for d
                                in dumpty_node.descendants.values()
                                if d.n_gram[-1] in ['sat', 'had'])
        self.assertAlmostEqual(
            beta_n_1 / denominator, math.exp(humpty_dumpty_node.log_alpha), 4)
        # alpha(dumpty)
        beta_n_1 = 1.0 - sum(d.p_star() for d in dumpty_node.descendants.values())
        denominator = 1.0 - sum(d.p_star() for d
                                in trie_node.descendants.values()
                                if d.n_gram[0] in ['sat', 'had', 'together'])
        self.assertAlmostEqual(
            beta_n_1 / denominator, math.exp(dumpty_node.log_alpha), 4)

    def test_p_katz_simple(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Dumpty together again.") # note we changed Humpty -> Dumpty
        trie_node = katzbackoff.compute_model(katzbackoff.populate_trie_nodes(f, 3), 3)
        model = katzbackoff.LanguageModel(trie_node, 3)
        p_katz = math.exp(model.log_p_katz(("humpty", "dumpty", "together")))
        humpty_dumpty_alpha = math.exp(trie_node.find_node(("humpty", "dumpty")).log_alpha)
        dumpty_together_p_star = trie_node.find_node(("dumpty", "together")).p_star()
        self.assertAlmostEqual(
            humpty_dumpty_alpha * dumpty_together_p_star, p_katz, 6)

    def test_p_katz_missing_prefix(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Dumpty together again.") # note we changed Humpty -> Dumpty
        trie_node = katzbackoff.compute_model(katzbackoff.populate_trie_nodes(f, 3), 3)
        model = katzbackoff.LanguageModel(trie_node, 3)
        p_katz = math.exp(model.log_p_katz(("couch", "cat", "sat")))
        self.assertAlmostEqual(
            trie_node.descendants['sat'].p_star(), p_katz, 6)

    def test_p_katz_missing_suffix(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Dumpty together again.") # note we changed Humpty -> Dumpty
        trie_node = katzbackoff.compute_model(katzbackoff.populate_trie_nodes(f, 3), 3)
        model = katzbackoff.LanguageModel(trie_node, 3)
        p_katz = math.exp(model.log_p_katz(("humpty", "dumpty", "stood")))
        self.assertAlmostEqual(trie_node.beta(), p_katz, 6)

    def test_p_katz_missing_complete(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Dumpty together again.") # note we changed Humpty -> Dumpty
        trie_node = katzbackoff.compute_model(katzbackoff.populate_trie_nodes(f, 3), 3)
        model = katzbackoff.LanguageModel(trie_node, 3)
        p_katz = math.exp(model.log_p_katz(("fat", "cat", "stood")))
        self.assertAlmostEqual(trie_node.beta(), p_katz, 6)

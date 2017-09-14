import katzbackoff
import unittest
import io

class LanguageModelTests(unittest.TestCase):
    def test_trie_nodes(self):
        f = io.StringIO(
            "Humpty Dumpty sat on a wall, "
            "Humpty Dumpty had a great fall; "
            "All the king's horses and all the king's men "
            "Couldn't put Humpty together again.")
        trie_nodes = katzbackoff.make_trie_nodes(f, 3, False)
        print(trie_nodes)

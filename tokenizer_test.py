import unittest
import io
import tokenizer

class TokenizeTests(unittest.TestCase):
    def test_text_0(self):
        f = io.StringIO(
            "Mr. Sherwood said reaction to Sea Containers' proposal "
            "has been \"very positive.\" In New York Stock Exchange composite "
            "trading yesterday, Sea Containers closed at $62.625, up 62.5 cents.")
        tokens = list(tokenizer.raw_tokenize(f))
        expected_tokens = [
            'mr.', 'sherwood', 'said', 'reaction', 'to', 'sea', 'containers',
            "'", 'proposal', 'has', 'been', '"', 'very', 'positive', '.', '"',
            'in', 'new', 'york', 'stock', 'exchange', 'composite', 'trading',
            'yesterday', ',', 'sea', 'containers', 'closed', 'at', '$62.625',
            ',', 'up', '62.5', 'cents', '.']
        self.assertEqual(tokens, expected_tokens)

    def test_text_1(self):
        f = io.StringIO("Don't 'do anything', holmes!")
        tokens = list(tokenizer.raw_tokenize(f))
        expected_tokens = ['do', 'not', "'", 'do', 'anything',
                           "'", ',', 'holmes', '!']
        self.assertEqual(tokens, expected_tokens)

    def test_text_2(self):
        f = io.StringIO(
            "My wife's proposal that we don't 'do anything' at all \n"
            "is something I haven't thought about just yet. Just go back "
            "to school and get a Ph.D. or an M.D., you know?")
        tokens = list(tokenizer.raw_tokenize(f))
        expected_tokens = ['my', 'wife', "'s", 'proposal', 'that', 'we',
                           'do', 'not', "'", 'do', 'anything', "'", 'at',
                           'all', 'is', 'something', 'i', 'have', 'not',
                           'thought', 'about', 'just', 'yet', '.', 'just',
                           'go', 'back', 'to', 'school', 'and', 'get', 'a',
                           'ph.d.', 'or', 'an', 'm.d.', ',', 'you', 'know', '?']
        self.assertEqual(tokens, expected_tokens)

    def test_tokenize(self):
        f = io.StringIO("Don't 'do anything', holmes!")
        tokens = list(tokenizer.tokenize(f, include_punctuation=True))
        expected_tokens = ['do', 'not', "'", 'do', 'anything',
                           "'", ',', 'holmes', '!']
        self.assertEqual(tokens, expected_tokens)
        f.seek(0)
        tokens = list(tokenizer.tokenize(f, include_punctuation=False))
        expected_tokens = ['do', 'not', 'do', 'anything', 'holmes']
        self.assertEqual(tokens, expected_tokens)

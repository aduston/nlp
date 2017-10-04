"""
From Norvig: http://www.norvig.com/spell-correct.html
"""

import os, re, string
from collections import Counter

letters = string.ascii_lowercase
_words = None

def find_words(text):
    return re.findall(r'\w+', text.lower())

def all_words():
    global _words
    if _words is None:
        _words = Counter(find_words(open(os.path.expanduser("~/big.txt")).read()))
    return _words

def all_candidates(word):
    return known([word]) | known(edits1(word)) | known(edits2(word))

def known(words):
    return set(w for w in words if w in all_words())

def edits1(word):
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if len(R) > 1]
    inserts = [L + c + R for L, R in splits for c in letters]
    replaces = [L + c + R[1:] for L, R in splits for c in letters]
    transpositions = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) >= 2]
    return set(deletes + inserts + replaces + transpositions)

def edits2(word):
    return (x for y in edits1(word) for x in edits1(y))

if __name__ == '__main__':
    print(all_candidates("acress"))

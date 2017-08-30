"""Tokenizer

This tokenization script is super-basic and essentially a direct port
of the script in chapter 3 of Jurafsky's NLP textbook, which is in turn
adapted from Grefenstette and Palmer.
"""

import re

LETTER_NUMBER = r"[a-z0-9]"
NOT_LETTER = r"[^a-z0-9]"
ALWAYS_SEP = r"[?!()\";/\|`]" # TODO: test these
CLITIC = "'|:|-|'s|'d|'m|'ll|'re|'ve|n't"
ABBREVS = set(["co.", "corp.", "vs.", "e.g.", "etc.", "ex.", "cf.",
               "eg.", "jan.", "feb.", "mar.",
               "apr.", "jun.", "jul.", "aug.", "sept.", "oct.", "nov.",
               "dec.", "ed.", "eds.", "repr.", "trans.", "vol.", "vols.",
               "rev.", "est.", "b.", "m.", "bur.", "d.", "r.", "m.", "dept.",
               "mm.", "u.", "mr.", "jr.", "ms.", "mme.", "mrs.", "dr.",
               "ph.d."])

def _ends_in_period(word):
    return re.search(r"{}\.".format(LETTER_NUMBER), word) is not None

def _is_abbreviation(word):
    if word in ABBREVS:
        return True
    if re.match(r"^[a-z]\.([a-z]\.)+$", word) is not None: # e.g. U.S.
        return True
    if re.match(r"^[a-z][bcdfghj-nptvxz]+$", word) is not None: # e.g. Inc.
        return True
    return False

def raw_tokenize(f):
    for line in f:
        line = line.lower()
        # put whitespace around unambiguous separators
        line = re.sub(ALWAYS_SEP, r" \g<0> ", line)
        # whitespace around commas that aren't inside numbers
        line = re.sub("([^0-9]),", r"\1 , ", line)
        line = re.sub(",([^0-9])", r" , \1", line)
        # distinguish singlequotes from apostrophes by segmenting off
        # single quotes not preceded by letter
        line = re.sub("^'", "' ", line)
        line = re.sub(r"({})'".format(NOT_LETTER), r"\1 ' ", line)
        # segment off unambiguous word-final clitics and punctuation
        line = re.sub("({})$".format(CLITIC), r" \1", line)
        line = re.sub("({})({})".format(CLITIC, NOT_LETTER), r" \1 \2", line)
        line = line.strip()
        possible_words = re.split(r"\s+", line)
        for word in possible_words:
            has_space = False
            if _ends_in_period(word) and not _is_abbreviation(word):
                word = re.sub(r"\.$", " .", word)
                has_space = True
            word = word.replace("'ve", "have")
            word = word.replace("'m", "am")
            word = word.replace("n't", "not")
            if has_space:
                for w in word.split(" "):
                    yield w
            else:
                yield word

def tokenize(f, include_punctuation=False):
    for word in raw_tokenize(f):
        if include_punctuation or re.search(LETTER_NUMBER, word) is not None:
            yield word

def detokenize(tokens):
    capitalize = True
    at_start = True
    text = []
    for token in tokens:
        if token == "<s>" or token == "":
            continue
        if re.search(LETTER_NUMBER, token[0]) is None:
            text.append(token)
            if token == ".":
                capitalize = True
        else:
            if not at_start:
                text.append(" ")
            else:
                at_start = False
            if capitalize:
                text.append(token.capitalize())
            else:
                text.append(token)
            capitalize = False
    return "".join(text)

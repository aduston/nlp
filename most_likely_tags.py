def save_most_likely_tags(corpus, fn):
    tags = {} # mapping of word -> { tag -> count }
    for sentence in corpus.sentences():
        for w in sentence:
            if w.word not in tags:
                tags[w.word] = {}
            tags[w.word][w.correct_tag] = tags[w.word].get(w.correct_tag, 0) + 1
    with open(fn, "w") as f:
        for word in tags.keys():
            most_likely_tag = max(
                tags[word].items(), key=lambda x: x[1])[0]
            f.write("{0}\t{1}\n".format(word, most_likely_tag))

def get_most_likely_tags(fn):
    most_likely_tags = {} # mapping of word -> tag
    with open(fn, 'r') as f:
        for line in f:
            word, tag = line.split("\t")
            most_likely_tags[word] = tag.rstrip()
    return most_likely_tags

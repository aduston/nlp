from tokenizer import tokenize

class CircularBuffer(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.pointer = 0
        self.data = []

    def add(self, obj):
        if len(self.data) < self.capacity:
            self.data.append(obj)
        else:
            self.data[self.pointer] = obj
            self.pointer = (self.pointer + 1) % self.capacity

    def make_snapshot_tuple(self):
        pass
        

def compute_n_gram(fn, n):
    """
    Computes n-grams on text in file name fn.
    """
    

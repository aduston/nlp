class Template(object):
    def __init__(self, z_spec, w_spec=None):
        self.z_spec = z_spec
        self.w_spec = w_spec

class TemplateInstanceCandidate(object):
    def __init__(self, z_set, w_set=None):
        self.z_set = z_set
        self.w_set = w_set

class TemplateInstance(object):
    def __init__(self, a, b, z, w=None):
        self.a = a
        self.b = b
        self.z = z
        self.w = w

TAGS = 

TEMPLATES = [ # same templates Brill used
    Template(-1),
    Template(-2),
    Template([-2, -1]),
    Template([1, 2]),
    Template([-3, -1]),
    Template([1, 3]),
    Template(-1, 1),
    Template(-1, -2),
    Template(-1, 2),
    Template(1, -2),
    Template(1, 2)
]

def get_best_instance(corpus, template):
    """
    Returns a (template_instance, score) pair.
    """
    

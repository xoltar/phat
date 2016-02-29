import _phat

class Namespace:
    def __init__(self, **kwargs):
        self.types = kwargs.copy()

    def __getattr__(self, name):
        return self.types[name]

    def __repr__(self):
        return "Namespace(%s)" % repr(list(self.types.keys()))

    def get_name(self, obj):
        for (k,v) in self.types.items():
            if v == obj:
                return k
        raise KeyError()



representations = Namespace(bit_tree_pivot_column = object(),
                            sparse_pivot_column = object(),
                            full_pivot_column = object(),
                            vector_vector = object(),
                            vector_heap = object(),
                            vector_set = object(),
                            vector_list = object())

reduction_algorithms = Namespace(twist_reduction = object())

def __short_name(name):
    return "".join([n[0] for n in name.split("_")])

def boundary_matrix(representation = representations.bit_tree_pivot_column):
    class_name = representations.get_name(representation)

    short_name = __short_name(class_name)

    function = getattr(_phat, "boundary_matrix_" + short_name)

    return function()

def compute_persistence_pairs(matrix,
                              reduction = reduction_algorithms.twist_reduction):

    class_name = matrix.__class__.__name__

    representation_short_name = class_name[len('boundary_matrix_'):]

    algo_name = reduction_algorithms.get_name(reduction)

    algo_short_name = __short_name(algo_name)

    function = getattr(_phat, "compute_persistence_pairs_" + representation_short_name + "_" + algo_short_name)

    return function(matrix)







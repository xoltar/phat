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

reductions = Namespace(twist_reduction = object(),
                       chunk_reduction = object(),
                       standard_reduction = object(),
                       row_reduction = object(),
                       spectral_sequence_reduction = object())

def __short_name(name):
    return "".join([n[0] for n in name.split("_")])

def convert(source, to_representation):
    class_name = source.__class__.__name__
    source_rep_short_name = class_name[len('boundary_matrix_'):]
    to_rep_short_name = __short_name(representations.get_name(to_representation))
    function = getattr(_phat, "convert_%s_to_%s" % (source_rep_short_name, to_rep_short_name))
    return function(source)

def boundary_matrix(representation = representations.bit_tree_pivot_column, source = None):
    if source:
        return convert(source, representation)
    else:
        class_name = representations.get_name(representation)
        short_name = __short_name(class_name)
        function = getattr(_phat, "boundary_matrix_" + short_name)
        return function()

def compute_persistence_pairs(matrix,
                              reduction = reductions.twist_reduction):
    class_name = matrix.__class__.__name__
    representation_short_name = class_name[len('boundary_matrix_'):]
    algo_name = reductions.get_name(reduction)
    algo_short_name = __short_name(algo_name)
    function = getattr(_phat, "compute_persistence_pairs_" + representation_short_name + "_" + algo_short_name)
    return function(matrix)

def compute_persistence_pairs_dualized(matrix,
                                       reduction = reductions.twist_reduction):
    class_name = matrix.__class__.__name__
    representation_short_name = class_name[len('boundary_matrix_'):]
    algo_name = reductions.get_name(reduction)
    algo_short_name = __short_name(algo_name)
    function = getattr(_phat, "compute_persistence_pairs_dualized_" + representation_short_name + "_" + algo_short_name)
    return function(matrix)







import _phat
import enum

from _phat import persistence_pairs

__all__ = ['boundary_matrix',
           'persistence_pairs',
           'compute_persistence_pairs',
           'compute_persistence_pairs_dualized']


"""Bindings for the Persistent Homology Algorithm Toolbox


Please see https://bitbucket.org/phat-code/phat for more information.
"""


class representations(enum.Enum):
    """Available representations for internal storage of columns in
    a `boundary_matrix`
    """
    bit_tree_pivot_column = 1
    sparse_pivot_column = 2
    full_pivot_column = 3
    vector_vector = 4
    vector_heap = 5
    vector_set = 6
    vector_list = 7

class reductions(enum.Enum):
    "Available reduction algorithms"
    twist_reduction = 1
    chunk_reduction = 2
    standard_reduction = 3
    row_reduction = 4
    spectral_sequence_reduction = 5

def __short_name(name):
    return "".join([n[0] for n in name.split("_")])

def convert(source, to_representation):
    """Internal - function to convert from one `boundary_matrix` implementation to another"""
    class_name = source.__class__.__name__
    source_rep_short_name = class_name[len('boundary_matrix_'):]
    to_rep_short_name = __short_name(to_representation.name)
    function = getattr(_phat, "convert_%s_to_%s" % (source_rep_short_name, to_rep_short_name))
    return function(source)

def boundary_matrix(representation = representations.bit_tree_pivot_column, source = None):
    """Returns an instance of a `boundary_matrix` class.
    The boundary matrix will use the specified implementation for storing its column data.
    If the `source` parameter is specified, it will be assumed to be another boundary matrix,
    whose data should be copied into the new matrix.
    """
    if source:
        return convert(source, representation)
    else:
        class_name = representation.name
        short_name = __short_name(class_name)
        function = getattr(_phat, "boundary_matrix_" + short_name)
        return function()

def compute_persistence_pairs(matrix,
                              reduction = reductions.twist_reduction):
    """Computes persistence pairs (birth, death) for the given boundary matrix."""
    class_name = matrix.__class__.__name__
    representation_short_name = class_name[len('boundary_matrix_'):]
    algo_name = reduction.name
    algo_short_name = __short_name(algo_name)
    function = getattr(_phat, "compute_persistence_pairs_" + representation_short_name + "_" + algo_short_name)
    return function(matrix)

def compute_persistence_pairs_dualized(matrix,
                                       reduction = reductions.twist_reduction):
    """Computes persistence pairs (birth, death) from the dualized form of the given boundary matrix."""
    class_name = matrix.__class__.__name__
    representation_short_name = class_name[len('boundary_matrix_'):]
    algo_name = reduction.name
    algo_short_name = __short_name(algo_name)
    function = getattr(_phat, "compute_persistence_pairs_dualized_" + representation_short_name + "_" + algo_short_name)
    return function(matrix)







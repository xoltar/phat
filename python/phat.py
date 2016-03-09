"""Bindings for the Persistent Homology Algorithm Toolbox

PHAT is a tool for algebraic topology. It can be used via phat.py to compute
persistent (co)homology from boundary matrices, using various reduction
algorithms and column data representations.

Please see https://bitbucket.org/phat-code/phat/python for more information.
"""

import _phat
import enum

from _phat import persistence_pairs

#The public API for the module

__all__ = ['boundary_matrix',
           'persistence_pairs',
           'compute_persistence_pairs',
           'compute_persistence_pairs_dualized']

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
    """Available reduction algorithms"""
    twist_reduction = 1
    chunk_reduction = 2
    standard_reduction = 3
    row_reduction = 4
    spectral_sequence_reduction = 5

class boundary_matrix:
    """Boundary matrices that store the shape information of a cell complex.
    """

    def __init__(self, representation = representations.bit_tree_pivot_column, source = None):
        """
        The boundary matrix will use the specified implementation for storing its
        column data. If the `source` parameter is specified, it will be assumed to
        be another boundary matrix, whose data should be copied into the new
        matrix.

        Parameters
        ----------

        representation : phat.representation, optional
            The type of column storage to use in the requested boundary matrix.
        source : phat.boundary_matrix, optional
            If provided, creates the requested matrix as a copy of the data and dimensions
            in `source`.

        Returns
        -------

        matrix : boundary_matrix
            An instance of a class that satisfies the boundary matrix protocol.
        """
        self._representation = representation
        if source:
            self._matrix = _convert(source)
        else:
            self._matrix = self.__matrix_for_representation(representation)()

    def __matrix_for_representation(self, representation):
        short_name = _short_name(representation.name)
        return getattr(_phat, "boundary_matrix_" + short_name)

    def __eq__(self, other):
        return self._matrix == other._matrix

    def get_col(self, index):
        """Returns the column at the requested index"""
        return self._matrix.get_col(index)

    def get_dim(self, index):
        """Returns the dimension for the requested column"""
        return self._matrix.get_dim(index)

    def get_num_cols(self):
        """Returns the number of columns in the boundary matrix"""
        return self._matrix.get_num_cols()

    def get_num_entries(self):
        """Returns the number of entries in the boundary matrix"""
        return self._matrix.get_num_entries()

    def get_vector_vector(self):
        """Returns the contents of the boundary matrix"""
        return self._matrix.get_vector_vector()

    def is_empty(self, index):
        """Is the given column empty?"""
        return self._matrix.is_empty(index)

    def load_vector_vector(self, columns, dimensions):
        """Loads the given data and dimensions into this boundary matrix"""
        return self._matrix.load_vector_vector(columns, dimensions)

    def load_binary(self, file_name):
        """Load this boundary matrix from a binary file"""
        return self._matrix.load_binary

    def save_binary(self, file_name):
        """Save this boundary matrix to a binary file"""
        return self._matrix.save_binary

    def load_ascii(self, file_name):
        """Load this boundary matrix from a text file"""
        return self._matrix.load_ascii

    def save_ascii(self, file_name):
        """Save this boundary matrix to a text file"""
        return self._matrix.save_ascii

    def set_col(self, index, column):
        """Set the column at the given index"""
        return self._matrix.set_col(index, column)

    def set_dims(self, dimensions):
        """Set the dimensions for this boundary matrix"""
        return self._matrix.set_dims(dimensions)

    def set_dim(self, index, dimension):
        """Sets the dimension at the given index"""
        return self._matrix.set_dim(index, dimension)

    def compute_persistence_pairs(self,
                                reduction = reductions.twist_reduction):
        """Computes persistence pairs (birth, death) for the given boundary matrix."""
        representation_short_name = _short_name(self._representation.name)
        algo_name = reduction.name
        algo_short_name = _short_name(algo_name)
        #Look up an implementation that matches the requested characteristics
        #in the _phat module
        function = getattr(_phat, "compute_persistence_pairs_" + representation_short_name + "_" + algo_short_name)
        return function(self._matrix)

    def compute_persistence_pairs_dualized(self, 
                                        reduction = reductions.twist_reduction):
        """Computes persistence pairs (birth, death) from the dualized form of the given boundary matrix."""
        representation_short_name = _short_name(self._representation.name)
        algo_name = reduction.name
        algo_short_name = _short_name(algo_name)
        #Look up an implementation that matches the requested characteristics
        #in the _phat module
        function = getattr(_phat, "compute_persistence_pairs_dualized_" + representation_short_name + "_" + algo_short_name)
        return function(self._matrix)

    def convert(self, representation):
        """Copy this matrix to another with a different representation"""
        return boundary_matrix(representation, self)

def _short_name(name):
    """An internal API that takes leading characters from words
    For instance, 'bit_tree_pivot_column' becomes 'btpc'
    """
    return "".join([n[0] for n in name.split("_")])

def _convert(source, to_representation):
    """Internal - function to convert from one `boundary_matrix` implementation to another"""
    class_name = source.__class__.__name__
    source_rep_short_name = class_name[len('boundary_matrix_'):]
    to_rep_short_name = _short_name(to_representation.name)
    function = getattr(_phat, "convert_%s_to_%s" % (source_rep_short_name, to_rep_short_name))
    return function(source)









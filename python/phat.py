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

class column:
    def __init__(self, matrix, index):
        self._matrix = matrix
        self._index = index

    @property
    def index(self):
        return self._index

    @property
    def dimension(self):
        return self._matrix._matrix.get_dim(self._index)

    @dimension.setter
    def dimension(self, value):
        return self._matrix._matrix.set_dim(self._index, value)

    @property
    def boundary(self):
        return self._matrix._matrix.get_col(self._index)

    @boundary.setter
    def boundary(self, values):
        return self._matrix._matrix.set_col(self._index, values)

class boundary_matrix:
    """Boundary matrices that store the shape information of a cell complex.
    """

    def __init__(self, representation = representations.bit_tree_pivot_column, source = None, columns = None):
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
            self._matrix = _convert(source, representation)
        else:
            self._matrix = self.__matrix_for_representation(representation)()
            if columns:
                self.columns = columns

    @property
    def columns(self):
        return [column(self, i) for i in range(self._matrix.get_num_cols())]

    @columns.setter
    def columns(self, columns):
        for col in columns:
           if not (isinstance(col, column) or isinstance(col, tuple)):
               raise TypeError("All columns must be column objects, or (dimension, values) tuples")
        if len(columns) != len(self.dimensions):
            self._matrix.set_dims([0] * len(columns))
        for i, col in enumerate(columns):
            if isinstance(col, column):
                self._matrix.set_dim(i, col.dimension)
                self._matrix.set_col(i, col.boundary)
            else:
                dimension, values = col
                self._matrix.set_dim(i, dimension)
                self._matrix.set_col(i, values)

    @property
    def dimensions(self):
        return [self.get_dim(i) for i in range(self._matrix.get_num_cols())]

    @dimensions.setter
    def dimensions(self, dimensions):
        return self._matrix.set_dims(dimensions)

    def __matrix_for_representation(self, representation):
        short_name = _short_name(representation.name)
        return getattr(_phat, "boundary_matrix_" + short_name)

    def __eq__(self, other):
        return self._matrix == other._matrix

    def __len__(self):
        return self._matrix.get_num_entries()

    #Pickle support
    def __getstate__(self):
        (dimensions, columns) = self._matrix.get_vector_vector()
        return (self._representation, dimensions, columns)

    #Pickle support
    def __setstate__(self, state):
        presentation, dimensions, columns = state
        self._representation = representation
        self._matrix = self.__matrix_for_representation(representation)
        self._matrix.set_vector_vector(dimensions, columns)

    def load(self, file_name, mode = 'b'):
        """Load this boundary matrix from a file"""
        if mode == 'b':
            return self._matrix.load_binary(file_name)
        elif mode == 't':
            return self._matrix.load_ascii(file_name)

    def save(self, file_name, mode = 'b'):
        """Save this boundary matrix to a file"""
        if mode == 'b':
            return self._matrix.save_binary(file_name)
        elif mode == 't':
            return self._matrix.save_ascii(file_name)

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
    class_name = source._representation.name
    source_rep_short_name = _short_name(class_name)
    to_rep_short_name = _short_name(to_representation.name)
    function = getattr(_phat, "convert_%s_to_%s" % (source_rep_short_name, to_rep_short_name))
    return function(source._matrix)




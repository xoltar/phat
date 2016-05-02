"""Bindings for the Persistent Homology Algorithm Toolbox

PHAT is a tool for algebraic topology. It can be used via phat.py to compute
persistent (co)homology from boundary matrices, using various reduction
algorithms and column data representations.

Here is a simple example of usage.

We will build an ordered boundary matrix of this simplicial complex consisting of a single triangle::

     3
     |\\
     | \\
     |  \\
     |   \\ 4
    5|    \\
     |     \\
     |  6   \\
     |       \\
     |________\\
     0    2    1

Now the code::

    import phat

    # define a boundary matrix with the chosen internal representation
    boundary_matrix = phat.boundary_matrix(representation = phat.representations.vector_vector)

    # set the respective columns -- (dimension, boundary) pairs
    boundary_matrix.columns = [ (0, []),
                                (0, []),
                                (1, [0,1]),
                                (0, []),
                                (1, [1,3]),
                                (1, [0,3]),
                                (2, [2,4,5])]

    # or equivalently,
    # boundary_matrix = phat.boundary_matrix(representation = ...,
    #                                        columns = ...)
    # would combine the creation of the matrix and
    # the assignment of the columns

    # print some information of the boundary matrix:
    print()
    print("The boundary matrix has %d columns:" % len(boundary_matrix.columns))
    for col in boundary_matrix.columns:
        s = "Column %d represents a cell of dimension %d." % (col.index, col.dimension)
        if (col.boundary):
            s = s + " Its boundary consists of the cells " + " ".join([str(c) for c in col.boundary])
        print(s)
    print("Overall, the boundary matrix has %d entries." % len(boundary_matrix))

    pairs = boundary_matrix.compute_persistence_pairs()

    pairs.sort()

    print()
    print("There are %d persistence pairs: " % len(pairs))
    for pair in pairs:
        print("Birth: %d, Death: %d" % pair)


Please see https://bitbucket.org/phat-code/phat/python for more information.
"""

import _phat
import enum

from _phat import persistence_pairs

#The public API for the module

__all__ = ['boundary_matrix',
           'persistence_pairs',
           'representations',
           'reductions']


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


class column(object):
    """A view on one column of data in a boundary matrix"""
    def __init__(self, matrix, index):
        """INTERNAL. Columns are created automatically by boundary matrices.
        There is no need to construct them directly"""
        self._matrix = matrix
        self._index = index

    @property
    def index(self):
        """The 0-based index of this column in its boundary matrix"""
        return self._index

    @property
    def dimension(self):
        """The dimension of the column (0 = point, 1 = line, 2 = triangle, etc.)"""
        return self._matrix._matrix.get_dim(self._index)

    @dimension.setter
    def dimension(self, value):
        return self._matrix._matrix.set_dim(self._index, value)

    @property
    def boundary(self):
        """The boundary values in this column, i.e. the other columns that this column is bounded by"""
        return self._matrix._matrix.get_col(self._index)

    @boundary.setter
    def boundary(self, values):
        return self._matrix._matrix.set_col(self._index, values)

    def __str__(self):
        return "(%d, %s)" % (self.dimension, self.boundary)

class boundary_matrix(object):
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
        columns : column list, or list of (dimension, boundary) tuples, optional
            If provided, loads these columns into the new boundary matrix. Note that
            columns will be loaded in the order given, not according to their ``index`` properties.

        Returns
        -------

        matrix : boundary_matrix
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
        """A collection of column objects"""
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
        """A collection of dimensions, equivalent to [c.dimension for c in self.columns]"""
        return [self._matrix.get_dim(i) for i in range(self._matrix.get_num_cols())]

    @dimensions.setter
    def dimensions(self, dimensions):
        return self._matrix.set_dims(dimensions)

    def __matrix_for_representation(self, representation):
        short_name = _short_name(representation.name)
        return getattr(_phat, "boundary_matrix_" + short_name)

    def __eq__(self, other):
        return self._matrix == other._matrix

    #Note Python 2.7 needs BOTH __eq__ and __ne__ otherwise you get things that
    #are both equal and not equal
    def __ne__(self, other):
        return self._matrix != other._matrix

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
        """Load this boundary matrix from a file

        Parameters
        ----------

        file_name : string
            The file name to load

        mode : string, optional (defaults to 'b')
            The mode ('b' for binary, 't' for text) to use for working with the file

        Returns
        -------

        success : bool

        """
        if mode == 'b':
            return self._matrix.load_binary(file_name)
        elif mode == 't':
            return self._matrix.load_ascii(file_name)
        else:
            raise ValueError("Only 'b' - binary and 't' - text modes are supported")

    def save(self, file_name, mode = 'b'):
        """Save this boundary matrix to a file

        Parameters
        ----------

        file_name : string
            The file name to load

        mode : string, optional (defaults to 'b')
            The mode ('b' for binary, 't' for text) to use for working with the file

        Returns
        -------

        success : bool

        """
        if mode == 'b':
            return self._matrix.save_binary(file_name)
        elif mode == 't':
            return self._matrix.save_ascii(file_name)
        else:
            raise ValueError("Only 'b' - binary and 't' - text modes are supported")

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




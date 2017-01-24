Persistent Homology Algorithm Toolkit (PHAT)
============================================

This is a Python interface for the `Persistent Homology Algorithm Toolkit`_, a software library
that contains methods for computing the persistence pairs of a 
filtered cell complex represented by an ordered boundary matrix with Z\ :sub:`2` coefficients.

For an introduction to persistent homology, see the textbook [1]_. This software package
contains code for several algorithmic variants:

* The "standard" algorithm (see [1]_, p.153)
* The "row" algorithm from [2]_ (called pHrow in that paper)
* The "twist" algorithm, as described in [3]_ (default algorithm)
* The "chunk" algorithm presented in [4]_ 
* The "spectral sequence" algorithm (see [1]_, p.166)

All but the standard algorithm exploit the special structure of the boundary matrix
to take shortcuts in the computation. The chunk and the spectral sequence algorithms
make use of multiple CPU cores if PHAT is compiled with OpenMP support.

All algorithms are implemented as function objects that manipulate a given 
``boundary_matrix`` (to be defined below) object to reduced form. 
From this reduced form one can then easily extract the persistence pairs. 
Alternatively, one can use the ``compute_persistence_pairs function`` which takes an 
algorithm as a parameter, reduces the given ``boundary_matrix`` and stores the 
resulting pairs in a given ``persistence_pairs`` object.

The ``boundary_matrix`` class takes a "Representation" class as a parameter. 
This representation defines how columns of the matrix are represented and how 
low-level operations (e.g., column additions) are performed. The right choice of the 
representation class can be as important for the performance of the program as choosing
the algorithm. We provide the following choices of representation classes:

* ``vector_vector``: Each column is represented as a sorted ``std::vector`` of integers, containing the indices of the non-zero entries of the column. The matrix itself is a ``std::vector`` of such columns.
* ``vector_heap``: Each column is represented as a heapified ``std::vector`` of integers, containing the indices of the non-zero entries of the column. The matrix itself is a ``std::vector`` of such columns.
* ``vector_set``: Each column is a ``std::set`` of integers, with the same meaning as above. The matrix is stored as a ``std::vector`` of such columns.
* ``vector_list``: Each column is a sorted ``std::list`` of integers, with the same meaning as above. The matrix is stored as a ``std::vector`` of such columns.
* ``sparse_pivot_column``: The matrix is stored as in the vector_vector representation. However, when a column is manipulated, it is first  converted into a ``std::set``, using an extra data field called the "pivot column".  When another column is manipulated later, the pivot column is converted back to  the ``std::vector`` representation. This can lead to significant speed improvements when many columns  are added to a given pivot column consecutively. In a multicore setup, there is one pivot column per thread.
* ``heap_pivot_column``: The same idea as in the sparse version. Instead of a ``std::set``, the pivot column is represented by a ``std::priority_queue``. 
* ``full_pivot_column``: The same idea as in the sparse version. However, instead of a ``std::set``, the pivot column is expanded into a bit vector of size n (the dimension of the matrix). To avoid costly initializations, the class remembers which entries have been manipulated for a pivot column and updates only those entries when another column becomes the pivot.
* ``bit_tree_pivot_column`` (default representation): Similar to the ``full_pivot_column`` but the implementation is more efficient. Internally it is a bit-set with fast iteration over nonzero elements, and fast access to the maximal element. 

Installation
------------

If you wish to use the released version of PHAT, you can simply install from PyPI::

    pip install phat

Installation from Source
------------------------
Suppose you have checked out the PHAT repository at location $PHAT. Then you can::

	cd $PHAT

    pip install .

This will install PHAT for whatever Python installation your ``pip`` executable is associated with.
Please ensure you use the ``pip`` that comes from the same directory where your ``python`` executable lives!

Currently, the PHAT Python bindings are known to work on:

* Linux with Python 2.7 (tested on Ubuntu 14.04 with system Python)
* Linux with Python 3.5 (tested on Ubuntu 14.04 with Anaconda)
* Mac OS X with Python 2.7.12 (tested on Sierra with homebrew)
* Mac OS X with Python 3.5 (tested on Sierra with homebrew)

Other configurations are untested.

Please note that this package DOES NOT work with the Python 2.7.10 that ships with the operating
system in Mac OS X. These words of wisdom from `python.org`_ are worth heeding:

    The version of Python that ships with OS X is great for learning but it’s not good for development.
    The version shipped with OS X may be out of date from the official current Python release,
    which is considered the stable production version.

We recommend installing Python on Mac OS X using either homebrew or Anaconda, according to your taste.

Please let us know if there is a platform you'd like us to support, we will do so if we can.

Sample usage
------------

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

    # or equivalently, boundary_matrix = phat.boundary_matrix(representation = ..., columns = ...)
    # would combine the creation of the matrix and the assignment of the columns

    # print some information of the boundary matrix:
    print("\nThe boundary matrix has %d columns:" % len(boundary_matrix.columns))
    for col in boundary_matrix.columns:
        s = "Column %d represents a cell of dimension %d." % (col.index, col.dimension)
        if (col.boundary):
            s = s + " Its boundary consists of the cells " + " ".join([str(c) for c in col.boundary])
        print(s)
    print("Overall, the boundary matrix has %d entries." % len(boundary_matrix))

    pairs = boundary_matrix.compute_persistence_pairs()

    pairs.sort()

    print("\nThere are %d persistence pairs: " % len(pairs))
    for pair in pairs:
        print("Birth: %d, Death: %d" % pair)

References:

.. [1] H.Edelsbrunner, J.Harer: Computational Topology, An Introduction. American Mathematical Society, 2010, ISBN 0-8218-4925-5
.. [2] V.de Silva, D.Morozov, M.Vejdemo-Johansson: Dualities in persistent (co)homology. Inverse Problems 27, 2011
.. [3] C.Chen, M.Kerber: Persistent Homology Computation With a Twist. 27th European Workshop on Computational Geometry, 2011.
.. [4] U.Bauer, M.Kerber, J.Reininghaus: Clear and Compress: Computing Persistent Homology in Chunks. arXiv:1303.0477_
.. _arXiv:1303.0477: http://arxiv.org/pdf/1303.0477.pdf
.. _`Persistent Homology Algorithm Toolkit`: https://bitbucket.org/phat/phat-code
.. _`python.org`:http://docs.python-guide.org/en/latest/starting/install/osx/

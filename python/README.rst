Persistent Homology Algorithm Toolkit (PHAT)
============================================

This software library contains methods for computing the persistence pairs of a 
filtered cell complex represented by an ordered boundary matrix with Z\ :sub:`2`\ coefficients.

For an introduction to persistent homology, see the textbook `[1]`. This software package
contains code for several algorithmic variants:

  * The "standard" algorithm (see `[1]`, p.153)
  * The "row" algorithm from `[2]` (called pHrow in that paper)
  * The "twist" algorithm, as described in `[3]` (default algorithm)
  * The "chunk" algorithm presented in `[4]` 
  * The "spectral sequence" algorithm (see `[1]`, p.166)

All but the standard algorithm exploit the special structure of the boundary matrix
to take shortcuts in the computation. The chunk and the spectral sequence algorithms
make use of multiple CPU cores if PHAT is compiled with OpenMP support.

All algorithms are implemented as function objects that manipulate a given 
`boundary_matrix` (to be defined below) object to reduced form. 
From this reduced form one can then easily extract the persistence pairs. 
Alternatively, one can use the `compute_persistence_pairs function` which takes an 
algorithm as a parameter, reduces the given `boundary_matrix` and stores the 
resulting pairs in a given `persistence_pairs` object.

The `boundary_matrix` class takes a "Representation" class as a parameter. 
This representation defines how columns of the matrix are represented and how 
low-level operations (e.g., column additions) are performed. The right choice of the 
representation class can be as important for the performance of the program as choosing
the algorithm. We provide the following choices of representation classes:

  * `vector_vector`: Each column is represented as a sorted `std::vector` of integers, containing the indices of the non-zero entries of the column. The matrix itself is a `std::vector` of such columns.
  * `vector_heap`: Each column is represented as a heapified `std::vector` of integers, containing the indices of the non-zero entries of the column. The matrix itself is a `std::vector` of such columns.
  * `vector_set`: Each column is a `std::set` of integers, with the same meaning as above. The matrix is stored as a `std::vector` of such columns.
  * `vector_list`: Each column is a sorted `std::list` of integers, with the same meaning as above. The matrix is stored as a `std::vector` of such columns.
  * `sparse_pivot_column`: The matrix is stored as in the vector_vector representation. However, when a column is manipulated, it is first  converted into a `std::set`, using an extra data field called the "pivot column".  When another column is manipulated later, the pivot column is converted back to  the `std::vector` representation. This can lead to significant speed improvements when many columns  are added to a given pivot column consecutively. In a multicore setup, there is one pivot column per thread.
  * `heap_pivot_column`: The same idea as in the sparse version. Instead of a `std::set`, the pivot column is represented by a `std::priority_queue`. 
  * `full_pivot_column`: The same idea as in the sparse version. However, instead of a `std::set`, the pivot column is expanded into a bit vector of size n (the dimension of the matrix). To avoid costly initializations, the class remembers which entries have been manipulated for a pivot column and updates only those entries when another column becomes the pivot.
  * `bit_tree_pivot_column` (default representation): Similar to the `full_pivot_column` but the implementation is more efficient. Internally it is a bit-set with fast iteration over nonzero elements, and fast access to the maximal element. 

Sample usage:
-------------

::
    print("""
    we will build an ordered boundary matrix of this simplicial complex consisting of a single triangle: 
    
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

     """)

    import phat

    # set the dimension of the cell that each column represents:
    dimensions = [0, 0, 1, 0, 1, 1, 2]

    # define a boundary matrix with the chosen internal representation
    boundary_matrix = phat.boundary_matrix(representation = phat.representations.vector_vector)

    # set the respective columns -- the columns entries have to be sorted
    boundary_matrix.set_dims(dimensions)
    boundary_matrix.set_col(0, [])
    boundary_matrix.set_col(1, [])
    boundary_matrix.set_col(2, [0,1])
    boundary_matrix.set_col(3, [])
    boundary_matrix.set_col(4, [1,3])
    boundary_matrix.set_col(5, [0,3])
    boundary_matrix.set_col(6, [2,4,5])

    # print some information of the boundary matrix:
    print()
    print("the boundary matrix has %d columns:" % boundary_matrix.get_num_cols())
    for col_idx in range(boundary_matrix.get_num_cols()):
        s = "column %d represents a cell of dimension %d." % (col_idx, boundary_matrix.get_dim(col_idx))
        if (not boundary_matrix.is_empty(col_idx)):
            s = s + " its boundary consists of the cells " + " ".join([str(c) for c in boundary_matrix.get_col(col_idx)])
        print(s)
    print("overall, the boundary matrix has %d entries." % boundary_matrix.get_num_entries())

    pairs = phat.compute_persistence_pairs(boundary_matrix)

    pairs.sort()

    print()

    print("there are %d persistence pairs: " % len(pairs))
    for pair in pairs:
        print("birth: %d, death: %d" % pair)

References:

1. H.Edelsbrunner, J.Harer: Computational Topology, An Introduction. American Mathematical Society, 2010, ISBN 0-8218-4925-5
2. V.de Silva, D.Morozov, M.Vejdemo-Johansson: Dualities in persistent (co)homology. Inverse Problems 27, 2011
3. C.Chen, M.Kerber: Persistent Homology Computation With a Twist. 27th European Workshop on Computational Geometry, 2011.
4. U.Bauer, M.Kerber, J.Reininghaus: Clear and Compress: Computing Persistent Homology in Chunks. [http://arxiv.org/pdf/1303.0477.pdf arXiv:1303.0477]

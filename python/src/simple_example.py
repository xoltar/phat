"""This file contains a simple example that demonstrates the usage of the library interface"""

if __name__ == "__main__":

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
    import numpy as np

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
    print("The boundary matrix has %d columns:" % boundary_matrix.get_num_cols())
    for col_idx in range(boundary_matrix.get_num_cols()):
        s = "Colum %d represents a cell of dimension %d." % (col_idx, boundary_matrix.get_dim(col_idx))
        if (not boundary_matrix.is_empty(col_idx)):
            s = s + " Its boundary consists of the cells " + " ".join([str(c) for c in boundary_matrix.get_col(col_idx)])
        print(s)
    print("Overall, the boundary matrix has %d entries." % boundary_matrix.get_num_entries())

    pairs = phat.compute_persistence_pairs(boundary_matrix)

    pairs.sort()

    print()

    print("There are %d persistence pairs: " % len(pairs))
    for pair in pairs:
        print("Birth: %d, Death: %d" % pair)

"""

# wrapper algorithm that computes the persistence pairs of a given boundary matrix using a specified algorithm
#include <phat/compute_persistence_pairs.h>

# main data structure (choice affects performance)
#include <phat/representations/vector_vector.h>

# algorithm (choice affects performance)
#include <phat/algorithms/standard_reduction.h>
#include <phat/algorithms/chunk_reduction.h>
#include <phat/algorithms/row_reduction.h>
#include <phat/algorithms/twist_reduction.h>
""" 

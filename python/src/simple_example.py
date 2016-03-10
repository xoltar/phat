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


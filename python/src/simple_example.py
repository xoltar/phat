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

    # set the dimension of the cell that each column represents:
    dimensions = [0, 0, 1, 0, 1, 1, 2]

    # define a boundary matrix with the chosen internal representation
    boundary_matrix = phat.boundary_matrix(representation = phat.representations.vector_vector)
    boundary_matrix.dimensions = dimensions

    # set the respective columns -- the columns entries have to be sorted
    boundary_matrix.columns[0].values = []
    boundary_matrix.columns[1].values = []
    boundary_matrix.columns[2].values = [0,1]
    boundary_matrix.columns[3].values = []
    boundary_matrix.columns[4].values = [1,3]
    boundary_matrix.columns[5].values = [0,3]
    boundary_matrix.columns[6].values = [2,4,5]


    # print some information of the boundary matrix:
    print()
    print("The boundary matrix has %d columns:" % len(boundary_matrix.dimensions))
    for col in boundary_matrix.columns:
        s = "Column %d represents a cell of dimension %d." % (col.index, col.dimension)
        if (col.values):
            s = s + " Its boundary consists of the cells " + " ".join([str(c) for c in col.values])
        print(s)
    print("Overall, the boundary matrix has %d entries." % boundary_matrix.get_num_entries())

    pairs = boundary_matrix.compute_persistence_pairs()

    pairs.sort()

    print()

    print("There are %d persistence pairs: " % len(pairs))
    for pair in pairs:
        print("Birth: %d, Death: %d" % pair)


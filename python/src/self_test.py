from __future__ import print_function
import sys
import phat

if __name__=='__main__':
    test_data = (sys.argv[1:] and sys.argv[1]) or "../../examples/torus.bin"

    print("Reading test data %s in binary format ..." % test_data)

    boundary_matrix = phat.boundary_matrix()
    # This is broken for some reason
    if not boundary_matrix.load(test_data):
        print("Error: test data %s not found!" % test_data)
        sys.exit(1)

    error = False

    def compute_chunked(mat):
        return mat.compute_persistence_pairs(phat.reductions.chunk_reduction)

    print("Comparing representations using Chunk algorithm ...")
    print("Running Chunk - Sparse ...")
    sparse_boundary_matrix = phat.boundary_matrix(phat.representations.sparse_pivot_column, boundary_matrix)
    sparse_pairs = compute_chunked(sparse_boundary_matrix)

    print("Running Chunk - Heap ...")
    heap_boundary_matrix = phat.boundary_matrix(phat.representations.vector_heap, boundary_matrix)
    heap_pairs = compute_chunked(heap_boundary_matrix)

    print("Running Chunk - Full ...")
    full_boundary_matrix = phat.boundary_matrix(phat.representations.full_pivot_column, boundary_matrix)
    full_pairs = compute_chunked(full_boundary_matrix)

    print("Running Chunk - BitTree ...")
    bit_tree_boundary_matrix = phat.boundary_matrix(phat.representations.bit_tree_pivot_column, boundary_matrix)
    bit_tree_pairs = compute_chunked(bit_tree_boundary_matrix)

    print("Running Chunk - Vec_vec ...")
    vec_vec_boundary_matrix = phat.boundary_matrix(phat.representations.vector_vector, boundary_matrix)
    vec_vec_pairs = compute_chunked(vec_vec_boundary_matrix)

    print("Running Chunk - Vec_heap ...")
    vec_heap_boundary_matrix = phat.boundary_matrix(phat.representations.vector_heap, boundary_matrix)
    vec_heap_pairs = compute_chunked(vec_heap_boundary_matrix)

    print("Running Chunk - Vec_set ...")
    vec_set_boundary_matrix = phat.boundary_matrix(phat.representations.vector_set, boundary_matrix)
    vec_set_pairs = compute_chunked(vec_set_boundary_matrix)

    print("Running Chunk - Vec_list ...")
    vec_list_boundary_matrix = phat.boundary_matrix(phat.representations.vector_list, boundary_matrix)
    vec_list_pairs = compute_chunked(vec_list_boundary_matrix)

    if sparse_pairs != heap_pairs:
        print("Error: sparse and heap differ!", file=sys.stderr)
        error = True
    if heap_pairs != full_pairs:
        print("Error: heap and full differ!", file=sys.stderr)
        error = True
    if full_pairs != vec_vec_pairs:
        print("Error: full and vec_vec differ!", file=sys.stderr)
        error = True
    if vec_vec_pairs != vec_heap_pairs:
        print("Error: vec_vec and vec_heap differ!", file=sys.stderr)
        error = True
    if vec_heap_pairs != vec_set_pairs:
        print("Error: vec_heap and vec_set differ!", file=sys.stderr)
        error = True
    if vec_set_pairs != bit_tree_pairs:
        print("Error: vec_set and bit_tree differ!", file=sys.stderr)
        error = True
    if bit_tree_pairs != vec_list_pairs:
        print("Error: bit_tree and vec_list differ!", file=sys.stderr)
        error = True
    if vec_list_pairs != sparse_pairs:
        print("Error: vec_list and sparse differ!", file=sys.stderr)
        error = True
    if error:
        sys.exit(1)
    else:
        print("All results are identical (as they should be)")

    print("Comparing algorithms using BitTree representation ...")
    print("Running Twist - BitTree ...")

    def bit_tree_mat():
        return phat.boundary_matrix(phat.representations.bit_tree_pivot_column, boundary_matrix)

    reps = phat.representations
    reds = phat.reductions
    def pairs(mat, red):
        return mat.compute_persistence_pairs(red)

    twist_boundary_matrix = bit_tree_mat()
    twist_pairs = pairs(twist_boundary_matrix, reds.twist_reduction)

    print("Running Standard - BitTree ...")
    std_boundary_matrix = bit_tree_mat()
    std_pairs = pairs(std_boundary_matrix, reds.standard_reduction)

    print("Running Chunk - BitTree ...")
    chunk_boundary_matrix = bit_tree_mat()
    chunk_pairs = pairs(chunk_boundary_matrix, reds.chunk_reduction)

    print("Running Row - BitTree ...")
    row_boundary_matrix = bit_tree_mat()
    row_pairs = pairs(row_boundary_matrix, reds.row_reduction)

    print("Running Spectral sequence - BitTree ...")
    ss_boundary_matrix = bit_tree_mat()
    ss_pairs = pairs(ss_boundary_matrix, reds.spectral_sequence_reduction)

    if twist_pairs != std_pairs:
        print("Error: twist and standard differ!", file=sys.stderr)
        error = True
    if std_pairs != chunk_pairs:
        print("Error: standard and chunk differ!", file=sys.stderr)
        error = True
    if chunk_pairs != row_pairs:
        print("Error: chunk and row differ!", file=sys.stderr)
        error = True
    if row_pairs != ss_pairs:
        print("Error: row and spectral sequence differ!", file=sys.stderr)
        error = True
    if ss_pairs != twist_pairs:
        print("Error: spectral sequence and twist differ!", file=sys.stderr)
        error = True
    if error:
        sys.exit(1)
    else:
         print("All results are identical (as they should be)")

    print("Comparing primal and dual approach using Chunk - Full ...")

    primal_boundary_matrix = phat.boundary_matrix(reps.full_pivot_column, boundary_matrix)
    primal_pairs = primal_boundary_matrix.compute_persistence_pairs(reds.chunk_reduction)

    dual_boundary_matrix = phat.boundary_matrix(reps.full_pivot_column, boundary_matrix)
    dual_pairs = dual_boundary_matrix.compute_persistence_pairs_dualized()

    if primal_pairs != dual_pairs:
        print("Error: primal and dual differ!", file=sys.stderr)
        error = True


    if error:
        sys.exit(1)
    else:
        print("All results are identical (as they should be)")

    print("Testing vector<vector> interface ...")

    vector_vector_boundary_matrix = phat.boundary_matrix(phat.representations.bit_tree_pivot_column)

    vector_vector_boundary_matrix.columns = boundary_matrix.columns

    if vector_vector_boundary_matrix != boundary_matrix:
        print("Error: [load|save]_vector_vector bug", file=sys.stderr)
        error = True

    if error:
        sys.exit(1)
    else:
        print("Test passed!")



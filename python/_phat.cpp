//Required header for using pybind11
#include <pybind11/pybind11.h>

//Automatic conversions of stl containers to Python ones
#include <pybind11/stl.h>

//Additional support for operators and numpy
#include <pybind11/operators.h>
#include <pybind11/numpy.h>

//All the things we're going to wrap
#include "phat/persistence_pairs.h"
#include "phat/compute_persistence_pairs.h"
#include "phat/boundary_matrix.h"
#include "phat/representations/abstract_pivot_column.h"
#include <phat/representations/vector_vector.h>
#include <phat/representations/vector_heap.h>
#include <phat/representations/vector_set.h>
#include <phat/representations/vector_list.h>
#include <phat/representations/sparse_pivot_column.h>
#include <phat/representations/heap_pivot_column.h>
#include <phat/representations/full_pivot_column.h>
#include <phat/representations/bit_tree_pivot_column.h>
#include <phat/algorithms/twist_reduction.h>
#include <phat/algorithms/standard_reduction.h>
#include <phat/algorithms/row_reduction.h>
#include <phat/algorithms/chunk_reduction.h>
#include <phat/algorithms/spectral_sequence_reduction.h>

namespace py = pybind11;

//## Some template functions we'll need later

// This function defines two Python functions in the extension module, that are named
// `compute_persistence_pairs_${rep}_${reduction}`
// `compute_persistence_pairs_dualized_${rep}_${reductionx}`.
//
// The Python user will never see these, since we will use (in phat.py) the type of the
// boundary matrix and the requested reduction to dispatch to the correct function
// required.
//
// These functions are the main operations of PHAT. In the Python version, they take
// a boundary matrix, and return a persistence_pairs object.
//
// `Reduction` will be an algorithm, `Representation` is a type that controls
// how the boundary matrix stores its internal state.
//
// We will be using this function to define these two functions for every combination
// of `Representation` and `Reduction` that PHAT supports.
template <typename Reduction, typename Representation>
void define_compute_persistence(py::module &mod,
                                const std::string &representation_suffix,
                                const std::string &reduction_suffix) {

  auto suffix = representation_suffix + std::string("_") + reduction_suffix;

  //We don't annotate these with doc strings or py::args because
  //they are only used internally by code in phat.py
  mod.def((std::string("compute_persistence_pairs_") + suffix).c_str(),
          [](phat::boundary_matrix<Representation> &matrix){
            phat::persistence_pairs pairs;
            phat::compute_persistence_pairs<Reduction>(pairs, matrix);
            return pairs;
          });
  mod.def((std::string("compute_persistence_pairs_dualized_") + suffix).c_str(),
          [](phat::boundary_matrix<Representation> &matrix){
            phat::persistence_pairs pairs;
            phat::compute_persistence_pairs_dualized<Reduction>(pairs, matrix);
            return pairs;
          });
}

// Define a function to convert a `boundary_matrix` with one internal representation to a
// `boundary_matrix` with a different internal representation. Like with define_compute_persistence,
// the user will never see this function, but it is used internally by phat.py.
template <typename SelfRep, typename OtherRep>
void define_converter(py::module &mod, const std::string &self_suffix, const std::string &other_suffix) {
  //We don't annotate these with doc strings or py::args because
  //they are only used internally by code in phat.py
  mod.def((std::string("convert_") + other_suffix + "_to_" + self_suffix).c_str(),
          [](phat::boundary_matrix<OtherRep> &other) {
            return phat::boundary_matrix<SelfRep>(other);
          });
}

// Creates a Python class for a `boundary_matrix<T>`. Boundary matrices are one of two important types
// used by PHAT.
template<class T>
void wrap_boundary_matrix(py::module &mod, const std::string &representation_suffix) {

  using mat = phat::boundary_matrix<T>;

  py::class_<mat>(mod, (std::string("boundary_matrix_") + representation_suffix).c_str())
    //Default no-args constructor
    .def(py::init())
    //#### Loading and extracting data from Python lists
    //Note we can use references to member functions (even templated ones) directly in many cases.
    .def("load_vector_vector",
         &mat::template load_vector_vector<phat::index, phat::dimension>,
         "Load this instance with the given columns and dimensions",
         py::arg("columns"), py::arg("dimensions"))
    .def("get_vector_vector", [](mat &m) {
        std::vector< std::vector< int > > vector_vector_matrix;
        std::vector< int > vector_dims;
        m.save_vector_vector( vector_vector_matrix, vector_dims );
        return std::tuple<std::vector<std::vector<int>>, std::vector<int>>(vector_vector_matrix, vector_dims);
      },
      "Extract the data in the boundary matrix into a list of columns, and a list of dimensions that correspond to the columns")
    //#### Loading and saving files
    .def("load_binary", &mat::load_binary,
         "Load this instance with data from a binary file")
    .def("save_binary", &mat::save_binary,
         "Save this instance to a binary file")
    .def("load_ascii", &mat::load_ascii,
         "Load this instance with data from a text file")
    .def("save_ascii", &mat::save_ascii,
         "Save this instance to a text file")
    //#### Getting and setting dimensions
    //Note that boundary_matrix dimensions are not normal matrix dimensions,
    //They refer to the dimension of the simplex stored in the given column.
    .def("get_dim", &mat::get_dim,
         "Get the dimension for the requested column.")
    .def("set_dim", &mat::set_dim, "Set the dimension for a single column",
         py::arg("index"), py::arg("dimension"))
    //The `set_dims` method is an example of making the data structure easier to use
    //from Python. This is a method that doesn't exist in the C++ class, but we add it
    //using a C++ lambda. This ability to enhance the binding using lambdas
    //is an *extremely* handy tool.
    .def("set_dims", [](mat &m, std::vector<phat::index> dims) {
        m.set_num_cols(dims.size());
        for(size_t i = 0; i < dims.size(); i++) {
          m.set_dim(i, dims[i]);
        }
      },
      "Set the dimension list for this boundary matrix",
      py::arg("dimensions"))

    //#### \__eq__
    //The `boundary_matrix<T>`'s `operator==` is templated, which could make a Python wrapper
    //very tricky indeed. Luckily, when we define multiple
    //methods with the same name but different C++ types, pybind11 will create a Python method
    //that chooses between them based on type tags that it manages. This is *also* extremely handy.
    .def("__eq__", &mat::template operator==<phat::bit_tree_pivot_column>)
    .def("__eq__", &mat::template operator==<phat::sparse_pivot_column>)
    .def("__eq__", &mat::template operator==<phat::heap_pivot_column>)
    .def("__eq__", &mat::template operator==<phat::full_pivot_column>)
    .def("__eq__", &mat::template operator==<phat::vector_vector>)
    .def("__eq__", &mat::template operator==<phat::vector_heap>)
    .def("__eq__", &mat::template operator==<phat::vector_set>)
    .def("__eq__", &mat::template operator==<phat::vector_list>)

    //Python 3.x can figure this out for itself, but Python 2.7 needs to be told:
    .def("__ne__", &mat::template operator!=<phat::bit_tree_pivot_column>)
    .def("__ne__", &mat::template operator!=<phat::sparse_pivot_column>)
    .def("__ne__", &mat::template operator!=<phat::heap_pivot_column>)
    .def("__ne__", &mat::template operator!=<phat::full_pivot_column>)
    .def("__ne__", &mat::template operator!=<phat::vector_vector>)
    .def("__ne__", &mat::template operator!=<phat::vector_heap>)
    .def("__ne__", &mat::template operator!=<phat::vector_set>)
    .def("__ne__", &mat::template operator!=<phat::vector_list>)

    //#### Data access

    // In `get_col`, since Python is garbage collected, the C++ idiom of passing in a collection
    // to load doesn't make much sense. We can simply allocate an STL vector and
    // return it. The pybind11 framework will take ownership and hook it into the
    // Python reference counting system.
    .def("get_col", [](mat &m, phat::index col_index) {
        std::vector<phat::index> col;
        m.get_col(col_index, col);
        return col;
      },
      "Extract a single column as a list",
      py::arg("index"))
         .def("set_col", &mat::set_col,
              "Set the values for a given column",
              py::arg("index"), py::arg("column"))
    .def("get_num_cols", &mat::get_num_cols)
    .def("is_empty", &mat::is_empty)
    .def("get_num_entries", &mat::get_num_entries);

  //#### Compute persistence
  // Define compute_persistence(_dualized) for all possible reductions.
  define_compute_persistence<phat::standard_reduction, T>(mod, representation_suffix, std::string("sr"));
  define_compute_persistence<phat::chunk_reduction, T>(mod, representation_suffix, std::string("cr"));
  define_compute_persistence<phat::row_reduction, T>(mod, representation_suffix, std::string("rr"));
  define_compute_persistence<phat::twist_reduction, T>(mod, representation_suffix, std::string("tr"));
  define_compute_persistence<phat::spectral_sequence_reduction, T>(mod, representation_suffix, std::string("ssr"));
  //#### Converters
  //Define functions to convert from this kind of `boundary_matrix` to any of the other types
  define_converter<T, phat::bit_tree_pivot_column>(mod, representation_suffix, std::string("btpc"));
  define_converter<T, phat::sparse_pivot_column>(mod, representation_suffix, std::string("spc"));
  define_converter<T, phat::heap_pivot_column>(mod, representation_suffix, std::string("hpc"));
  define_converter<T, phat::full_pivot_column>(mod, representation_suffix, std::string("fpc"));
  define_converter<T, phat::vector_vector>(mod, representation_suffix, std::string("vv"));
  define_converter<T, phat::vector_heap>(mod, representation_suffix, std::string("vh"));
  define_converter<T, phat::vector_set>(mod, representation_suffix, std:: string("vs"));
  define_converter<T, phat::vector_list>(mod, representation_suffix, std::string("vl"));
}
//fix_index checks for out-of-bounds indexes, and converts negative indices to positive ones
//e.g. pairs[-1] => pairs[len(pairs) - 1]
phat::index fix_index(const phat::persistence_pairs &p, int index) {
  //Note get_num_pairs returns type index, which is not unsigned, though it comes from
  //std::vector.size, which is size_t.
  phat::index pairs = p.get_num_pairs();
  assert(pairs > 0);
  if (index < 0) {
    index = pairs + index;
  }
  if ((index < 0) || static_cast<size_t>(index) >= static_cast<size_t>(pairs)) {
    //pybind11 helpfully converts C++ exceptions into Python ones
    throw py::index_error();
  }
  return index;
}

//Here we define the wrapper for the persistence_pairs class. Unlike `boundary_matrix`, this
//class is not templated, so is simpler to wrap.
void wrap_persistence_pairs(py::module &m) {
  py::class_<phat::persistence_pairs>(m, "persistence_pairs")
    //No-args constructor
    .def(py::init())

    //This is a method that takes two ints
    .def("append_pair",
         &phat::persistence_pairs::append_pair,
         "Appends a single (birth, death) pair",
         py::arg("birth"), py::arg("death"))

    //This is a method that takes two ints
    .def("set_pair",
         &phat::persistence_pairs::set_pair,
         "Sets the (birth, death) pair at a given index",
         py::arg("index"), py::arg("birth"), py::arg("death"))

    //#### Python collection support
    .def("__len__", &phat::persistence_pairs::get_num_pairs)
    // Unlike set_pair, this takes a Python 2-tuple
    .def("__setitem__",
         [](phat::persistence_pairs &p, int index, std::pair<phat::index,phat::index> pair) {
           phat::index idx = fix_index(p, index);
           p.set_pair(idx, pair.first, pair.second);
         })
    // \__len\__ and \__getitem\__ together serve to make this a Python iterable
    // so you can do `for i in pairs: blah`. A nicer way is to support \__iter\__,
    // which we leave for future work.
    .def("__getitem__", [](const phat::persistence_pairs &p, int index) {
        phat::index idx = fix_index(p, index);
        return p.get_pair(idx);
      })
    .def("clear", &phat::persistence_pairs::clear, "Empties the collection")
    .def("sort", &phat::persistence_pairs::sort, "Sort in place")
    .def("__eq__", &phat::persistence_pairs::operator==)
    .def("__ne__", [](phat::persistence_pairs &p, phat::persistence_pairs &other) {
        return p != other;
      })
    //#### File operations
    .def("load_ascii", &phat::persistence_pairs::load_ascii,
         "Load the contents of a text file into this instance")
    .def("save_ascii", &phat::persistence_pairs::save_ascii,
         "Save this instance to a text file")
    .def("save_binary", &phat::persistence_pairs::save_binary,
         "Save the contents of this instance to a binary file")
    .def("load_binary", &phat::persistence_pairs::load_binary,
         "Load the contents of a binary file into this instance");
}

//## Define the module
//This is where we actually define the `_phat` module. We'll also have a `phat` module that's written
//in Python, which will use `_phat` as an implementation detail.
PYBIND11_PLUGIN(_phat) {
  //Create the module object. First arg is the name, second is the module docstring.
  py::module m("_phat", "C++ wrapper for PHAT. Please use the phat module, not the _phat module");

  //Wrap the `persistence_pairs` class
  wrap_persistence_pairs(m);

  //#### Generate all the different representations of `boundary_matrix`
  wrap_boundary_matrix<phat::bit_tree_pivot_column>(m, "btpc");
  wrap_boundary_matrix<phat::sparse_pivot_column>(m, "spc");
  wrap_boundary_matrix<phat::heap_pivot_column>(m, "hpc");
  wrap_boundary_matrix<phat::full_pivot_column>(m, "fpc");
  wrap_boundary_matrix<phat::vector_vector>(m, "vv");
  wrap_boundary_matrix<phat::vector_heap>(m, "vh");
  wrap_boundary_matrix<phat::vector_set>(m, "vs");
  wrap_boundary_matrix<phat::vector_list>(m, "vl");

  //We're done!
  return m.ptr();

}

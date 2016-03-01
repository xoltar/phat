#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/numpy.h>

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

template <typename Reduction, typename Representation>
void define_compute_persistence(py::module &mod,
                                const std::string &representation_suffix,
                                const std::string &reduction_suffix) {

  auto suffix = representation_suffix + std::string("_") + reduction_suffix;

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


template<class T>
void wrap_boundary_matrix(py::module &mod, const std::string &representation_suffix) {

  using mat = phat::boundary_matrix<T>;

  py::class_<mat>(mod, (std::string("boundary_matrix_") + representation_suffix).c_str())
    .def(py::init())
    .def("load_vector_vector", &mat::template load_vector_vector<phat::index, phat::dimension>)
    .def("load_ascii", &mat::load_ascii)
    .def("save_ascii", &mat::save_ascii)
    .def("get_dim", &mat::get_dim)
    .def("set_dim", &mat::set_dim)
    .def("set_dims", [](mat &m, std::vector<phat::index> dims) {
        m.set_num_cols(dims.size());
        for(int i = 0; i < dims.size(); i++) {
          m.set_dim(i, dims[i]);
        }
      })
    .def("is_empty", &mat::is_empty)
    .def("get_col", [](mat &m, phat::index col_index) {
        std::vector<phat::index> col;
        m.get_col(col_index, col);
        return col;
      })
    .def("set_col", &mat::set_col)
    .def("get_num_cols", &mat::get_num_cols)
    .def("get_num_entries", &mat::get_num_entries);

  define_compute_persistence<phat::standard_reduction, T>(mod, representation_suffix, std::string("sr"));
  define_compute_persistence<phat::chunk_reduction, T>(mod, representation_suffix, std::string("cr"));
  define_compute_persistence<phat::row_reduction, T>(mod, representation_suffix, std::string("rr"));
  define_compute_persistence<phat::twist_reduction, T>(mod, representation_suffix, std::string("tr"));
  define_compute_persistence<phat::spectral_sequence_reduction, T>(mod, representation_suffix, std::string("ssr"));
}

PYBIND11_PLUGIN(_phat) {
  py::module m("_phat", "pybind11 example plugin");

  py::class_<phat::persistence_pairs>(m, "persistence_pairs")
    .def(py::init())
    .def("__len__", &phat::persistence_pairs::get_num_pairs)
    .def("append_pair", &phat::persistence_pairs::append_pair)
    .def("set_pair", &phat::persistence_pairs::set_pair)
    .def("__setitem__",
         [](phat::persistence_pairs &p, int index, std::pair<phat::index,phat::index> &pair) {
           if (index >= p.get_num_pairs()) {
             throw py::index_error();
           }
           p.set_pair(index, pair.first, pair.second);
         })
    .def("__getitem__", [](const phat::persistence_pairs &p, size_t index) {
        if (index >= p.get_num_pairs()) {
          throw py::index_error();
        }
        return p.get_pair(index);
      })
    .def("clear", &phat::persistence_pairs::clear)
    .def("load_ascii", &phat::persistence_pairs::load_ascii)
    .def("save_ascii", &phat::persistence_pairs::save_ascii)
    .def("save_binary", &phat::persistence_pairs::save_binary)
    .def("load_binary", &phat::persistence_pairs::load_binary)
    .def("sort", &phat::persistence_pairs::sort)
    .def("__eq__", &phat::persistence_pairs::operator==);


  wrap_boundary_matrix<phat::bit_tree_pivot_column>(m, "btpc");
  wrap_boundary_matrix<phat::sparse_pivot_column>(m, "spc");
  wrap_boundary_matrix<phat::heap_pivot_column>(m, "hpc");
  wrap_boundary_matrix<phat::full_pivot_column>(m, "fpc");
  wrap_boundary_matrix<phat::vector_vector>(m, "vv");
  wrap_boundary_matrix<phat::vector_heap>(m, "vh");
  wrap_boundary_matrix<phat::vector_set>(m, "vs");
  wrap_boundary_matrix<phat::vector_list>(m, "vl");

  using mat = phat::boundary_matrix<phat::bit_tree_pivot_column>;
  return m.ptr();

}

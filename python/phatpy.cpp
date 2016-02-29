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


// namespace {
//     // Special iterator data structure for python
//     struct PySequenceIterator {
//         PySequenceIterator(const Sequence &seq, py::object ref) : seq(seq), ref(ref) { }

//         float next() {
//             if (index == seq.size())
//                 throw py::stop_iteration();
//             return seq[index++];
//         }

//         const Sequence &seq;
//         py::object ref; // keep a reference
//         size_t index = 0;
//     };
// };

// void init_ex6(py::module &m) {

//     seq.def(py::init<size_t>())
//        .def(py::init<const std::vector<float>&>())
//        /// Bare bones interface
//        .def("__getitem__", [](const Sequence &s, size_t i) {
//             if (i >= s.size())
//                 throw py::index_error();
//             return s[i];
//         })
//        .def("__setitem__", [](Sequence &s, size_t i, float v) {
//             if (i >= s.size())
//                 throw py::index_error();
//             s[i] = v;
//         })
//        .def("__len__", &Sequence::size)
//        /// Optional sequence protocol operations
//        .def("__iter__", [](py::object s) { return PySequenceIterator(s.cast<const Sequence &>(), s); })
//        .def("__contains__", [](const Sequence &s, float v) { return s.contains(v); })
//        .def("__reversed__", [](const Sequence &s) -> Sequence { return s.reversed(); })
//        /// Slicing protocol (optional)
//        .def("__getitem__", [](const Sequence &s, py::slice slice) -> Sequence* {
//             py::ssize_t start, stop, step, slicelength;
//             if (!slice.compute(s.size(), &start, &stop, &step, &slicelength))
//                 throw py::error_already_set();
//             Sequence *seq = new Sequence(slicelength);
//             for (int i=0; i<slicelength; ++i) {
//                 (*seq)[i] = s[start]; start += step;
//             }
//             return seq;
//         })
//        .def("__setitem__", [](Sequence &s, py::slice slice, const Sequence &value) {
//             py::ssize_t start, stop, step, slicelength;
//             if (!slice.compute(s.size(), &start, &stop, &step, &slicelength))
//                 throw py::error_already_set();
//             if ((size_t) slicelength != value.size())
//                 throw std::runtime_error("Left and right hand size of slice assignment have different sizes!");
//             for (int i=0; i<slicelength; ++i) {
//                 s[start] = value[i]; start += step;
//             }
//         })
//        /// Comparisons
//        .def(py::self == py::self)
//        .def(py::self != py::self);
//        // Could also define py::self + py::self for concatenation, etc.

//     py::class_<PySequenceIterator>(seq, "Iterator")
//         .def("__iter__", [](PySequenceIterator &it) -> PySequenceIterator& { return it; })
//         .def("__next__", &PySequenceIterator::next);
// }

template <typename Reduction, typename Representation>
void define_compute_persistence(py::module &mod,
                                const std::string &representation_suffix,
                                const char * reduction_suffix) {
  using mat = phat::boundary_matrix<Representation>;
  mod.def((std::string("compute_persistence_pairs_") +
           representation_suffix +
           std::string("_") + std::string(reduction_suffix)).c_str() , [](mat &matrix){
            phat::persistence_pairs pairs;
            phat::compute_persistence_pairs<Reduction>(pairs, matrix);
            return pairs;
          });
}
template<class T>
void wrap_boundary_matrix(py::module &mod, const char * representation_suffix) {

  using mat = phat::boundary_matrix<T>;

  py::class_<mat>(mod, (std::string("boundary_matrix_") + std::string(representation_suffix)).c_str())
    // .def("__init__", [](mat &m, std::vector<phat::dimension> dims, py::array_t<phat::index> b) {
    //     /* Request a buffer descriptor from Python */
    //     py::buffer_info info = b.request();

    //     if (info.ndim != 2)
    //       throw std::runtime_error("Incompatible buffer dimension!");

    //     new (&m) mat;
    //     m.set_num_cols(dims.size());
    //     for(unsigned int i = 0; i < dims.size(); i++) {
    //       m.set_dim(0, dims[i]);
    //     }
    //     phat::column col(info.shape[0]);
    //     for(unsigned int c = 0; c < info.shape[1]; c++) {
    //       col.clear();
    //       for(unsigned int r = 0; r < info.shape[0]; r++) {
    //         col.push_back(((phat::index*)info.ptr)[(r * info.shape[1]) + c]);
    //       }
    //       m.set_col(c, col);
    //     }
    //   })
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

  define_compute_persistence<phat::standard_reduction, T>(mod, representation_suffix, "sr");
  define_compute_persistence<phat::chunk_reduction, T>(mod, representation_suffix, "cr");
  define_compute_persistence<phat::row_reduction, T>(mod, representation_suffix, "rr");
  define_compute_persistence<phat::twist_reduction, T>(mod, representation_suffix, "tr");
  define_compute_persistence<phat::spectral_sequence_reduction, T>(mod, representation_suffix, "ssr");
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
             //This exception isn't getting caught for some reason
             throw py::index_error();
           }
           p.set_pair(index, pair.first, pair.second);
         })
    .def("__getitem__", [](const phat::persistence_pairs &p, size_t index) {
        if (index >= p.get_num_pairs()) {
          //This exception isn't getting caught for some reason
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

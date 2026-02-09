#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "rack.hpp"
#include "scorer.hpp"
#include "item.hpp"

namespace py = pybind11;

PYBIND11_MODULE(fil_rouge_py, m)
{
    m.doc() = "Fil Rouge - Warehouse optimizer";

    py::class_<Coord>(m, "Coord")
        .def(py::init<>())
        .def_readwrite("x", &Coord::x)
        .def_readwrite("y", &Coord::y);

    py::class_<Slot>(m, "Slot")
        .def(py::init<>());

    py::class_<Rack>(m, "Rack")
        .def(py::init());

    py::class_<Scorer>(m, "Scorer")
        .def(py::init<int>(), py::arg("n")) // Bind le constructeur avec l'argument n
        .def("score", &Scorer::score, "Calcule le score de la solution", py::arg("python_solution"))
        .def("resize", &Scorer::resize, "Change la taille de l'entrée", py::arg("new_size"));
}

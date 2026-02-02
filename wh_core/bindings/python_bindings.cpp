#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "rack.hpp"

namespace py = pybind11;

PYBIND11_MODULE(fil_rouge_py, m)
{
    m.doc() = "Fil Rouge - Warehouse optimizer";

    py::class_<Coord>(m, "Coord")
        .def(py::init<>())
        .def_readwrite("x", &Coord::x)
        .def_readwrite("y", &Coord::y);

    py::class_<Slot>(m, "Slot")
        .def(py::init<>())
        .def_readwrite("xy", &Slot::xy);

    py::class_<Rack>(m, "Rack")
        .def(py::init());
    m.def(
        "f",
        &f,
        "Test",
        py::arg("x"));
}

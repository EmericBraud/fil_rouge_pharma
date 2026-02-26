#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "warehouse_engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(fil_rouge_py, m)
{
    m.doc() = "Fil Rouge - Warehouse optimizer";

    py::class_<WarehouseEngine>(m, "WarehouseEngine")
        .def(py::init())
        .def("evaluate_order", &WarehouseEngine::evaluate_order, "Calcule le score de la solution", py::arg("medicament_ids"))
        .def("get_size", &WarehouseEngine::get_size, "Retourne le nombre de médicaments à trier");
}

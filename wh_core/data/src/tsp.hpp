#pragma once
#include "graph.hpp"
#include <vector>

std::vector<std::vector<double>> build_distance_matrix(
    const WarehouseGraph& g,
    const std::vector<int>& nodes
);

double compute_path_cost(
    const std::vector<std::vector<double>>& matrix,
    const std::vector<int>& order
);
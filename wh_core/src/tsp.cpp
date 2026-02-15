#include "tsp.hpp"
#include "dijkstra.hpp"
#include <limits>

std::vector<std::vector<double>> build_distance_matrix(
    const WarehouseGraph& g,
    const std::vector<int>& nodes
) {
    int m = nodes.size();

    std::vector<std::vector<double>> matrix(
        m, std::vector<double>(m, std::numeric_limits<double>::infinity())
    );

    for (int i = 0; i < m; ++i) {

        std::vector<double> dist = dijkstra(g, nodes[i]);

        for (int j = 0; j < m; ++j) {
            matrix[i][j] = dist[nodes[j]];
        }
    }

    return matrix;
}

double compute_path_cost(
    const std::vector<std::vector<double>>& matrix,
    const std::vector<int>& item_order
) {
    if (item_order.empty()) return matrix[0][matrix.size() - 1];

    double total = 0.0;

    int start_index = 0;
    int end_index   = matrix.size() - 1;

    total += matrix[start_index][item_order[0]];

    for (int i = 0; i < item_order.size() - 1; ++i) {
        total += matrix[item_order[i]][item_order[i + 1]];
    }

    total += matrix[item_order.back()][end_index];

    return total;
}
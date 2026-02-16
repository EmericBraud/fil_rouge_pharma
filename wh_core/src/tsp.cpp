#include "tsp.hpp"
#include "dijkstra.hpp"
#include <limits>
#include <unordered_set>
#include <stdexcept>

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
    int n = matrix.size();
    int start_index = 0;
    int end_index   = n - 1;

    if (item_order.empty())
        return matrix[start_index][end_index];

    std::unordered_set<int> visited;

    for (int idx : item_order) {

        if (idx <= start_index || idx >= end_index) {
            throw std::invalid_argument(
                "Invalid node index in item_order"
            );
        }

        if (!visited.insert(idx).second) {
            throw std::invalid_argument(
                "Duplicate node detected in item_order"
            );
        }
    }

    double total = 0.0;

    total += matrix[start_index][item_order[0]];

    for (size_t i = 0; i + 1 < item_order.size(); ++i) {
        total += matrix[item_order[i]][item_order[i + 1]];
    }

    total += matrix[item_order.back()][end_index];

    return total;
}
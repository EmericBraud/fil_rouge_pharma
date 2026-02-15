#include <iostream>
#include <iomanip>
#include "warehouse_graph.hpp"
#include "graph.hpp"
#include "tsp.hpp"

int main() {
    WarehouseGraph warehouse = buildWarehouseGraph();

    std::cout << "===== AVANT INSERTION =====\n";

    for(int i = 0; i < warehouse.size(); ++i) {
        std::cout << "Noeud " << i << " voisins:\n";
        for(const auto& e : warehouse.neighbors(i)) {
            std::cout << "  vers " << e.to << " distance " << e.dist << "\n";
        }
    }

    int item1 = warehouse.insert_node_between(2, 4, 30.0, 80.0);
    int item2 = warehouse.insert_node_between(5, 6, 20.0, 40.0);
    int item3 = warehouse.insert_node_between(8, 9, 10.0, 60.0);

    std::cout << "\n===== APRES INSERTION =====\n";

    for(int i = 0; i < warehouse.size(); ++i) {
        std::cout << "Noeud " << i << " voisins:\n";
        for(const auto& e : warehouse.neighbors(i)) {
            std::cout << "  vers " << e.to << " distance " << e.dist << "\n";
        }
    }

    std::vector<int> nodes;

    nodes.push_back(0);
    nodes.push_back(item1);
    nodes.push_back(item2);
    nodes.push_back(item3);
    nodes.push_back(34);

    std::vector<std::vector<double>> matrix = build_distance_matrix(warehouse, nodes);

    std::cout << "\n===== MATRICE DES DISTANCES =====\n\n";

    for (int i = 0; i < matrix.size(); ++i) {
        for (int j = 0; j < matrix[i].size(); ++j) {
            std::cout << std::setw(8) << matrix[i][j] << " ";
        }
        std::cout << "\n";
    }

    return 0;
}
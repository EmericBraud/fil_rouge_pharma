#include "warehouse_engine.hpp"
#include "tsp.hpp"
#include <nlohmann/json.hpp>
#include <fstream>
#include <stdexcept>
#include <iostream>

using json = nlohmann::json;

WarehouseEngine::WarehouseEngine()
    : warehouse(buildWarehouseGraph()){}

void WarehouseEngine::load_locations(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) throw std::runtime_error("Cannot open file: " + filename);

    json j;
    file >> j;

    for (const auto& entry : j) {
        Location loc;
        loc.id = entry.at("id").get<int>();
        loc.u  = entry.at("u").get<int>();
        loc.v  = entry.at("v").get<int>();
        loc.dist_u = entry.at("dist_u").get<double>();
        loc.dist_v = entry.at("dist_v").get<double>();

        location_table[loc.id] = loc;
    }
}

void WarehouseEngine::load_medicament_mapping(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) throw std::runtime_error("Cannot open file: " + filename);

    json j;
    file >> j;

    for (const auto& entry : j) {
        int medicament_id = entry.at("medicament_id").get<int>();
        int location_id   = entry.at("location_id").get<int>();

        if (location_table.find(location_id) == location_table.end())
            throw std::runtime_error("Location id not found for medicament " + std::to_string(medicament_id));

        medicament_to_location[medicament_id] = location_id;
    }
}

double WarehouseEngine::evaluate_order(const std::vector<int>& medicament_ids) {
    std::vector<int> tsp_nodes;

    int start_node = 0;
    int end_node   = 34;
    tsp_nodes.push_back(start_node);

    for (int med_id : medicament_ids) {
        if (medicament_to_location.find(med_id) == medicament_to_location.end())
            throw std::runtime_error("Unknown medicament id: " + std::to_string(med_id));

        int loc_id = medicament_to_location[med_id];
        const Location& loc = location_table.at(loc_id);

        static std::unordered_map<int, int> inserted_nodes;
        int node_number;
        if (inserted_nodes.find(loc_id) != inserted_nodes.end()) {
            node_number = inserted_nodes[loc_id];
        } else {
            node_number = warehouse.insert_node_between(loc.u, loc.v, loc.dist_u, loc.dist_v);
            inserted_nodes[loc_id] = node_number;
        }

        tsp_nodes.push_back(node_number);
    }

    tsp_nodes.push_back(end_node);

    std::vector<std::vector<double>> matrix = build_distance_matrix(warehouse, tsp_nodes);

    return compute_path_cost(matrix, std::vector<int>(tsp_nodes.begin() + 1, tsp_nodes.end() - 1));
}
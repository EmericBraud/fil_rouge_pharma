#include "warehouse_engine.hpp"
#include "tsp.hpp"
#include "dijkstra.hpp"
#include <nlohmann/json.hpp>
#include <fstream>
#include <stdexcept>
#include <iostream>
#include <string_view>
#include <filesystem>
#include <ranges>
#include <algorithm>
#include <cassert>
#include <unordered_set>

using json = nlohmann::json;
namespace fs = std::filesystem;

constexpr char locations_file[] = "data/locations.json";
constexpr char medicament_locations_file[] = "data/medicament_locations.json";

WarehouseEngine::WarehouseEngine()
    : warehouse(buildWarehouseGraph()), size(0)
{
    load_files();
    warehouse.export_graph_to_dot("step1.dot");

    std::vector<std::pair<int, int>> rangees;
    std::vector<int> temp_matrix_nodes; // Pour stocker les ID de nœuds insérés

    for (auto &location_pair : location_table)
    {
        int loc_id = location_pair.first;
        auto &location = location_pair.second;

        // Harmonisation : on s'assure que u est le plus petit
        if (location.u > location.v)
        {
            std::swap(location.u, location.v);
            std::swap(location.dist_u, location.dist_v);
        }

        // Insertion et récupération de l'ID du nœud créé
        int node_id = warehouse.insert_node_between(location.u, location.v, location.dist_u, location.dist_v);

        // On sauvegarde les relations pour evaluate_order
        location_to_node[loc_id] = node_id;
        temp_matrix_nodes.push_back(node_id);

        int u = location.u;
        int v = location.v;
        if (!std::ranges::contains(rangees, std::pair<int, int>(u, v)))
        {
            rangees.push_back({u, v});
        }
    }
    warehouse.export_graph_to_dot("step2.dot");

    for (auto pair : rangees)
    {
        int u = pair.first;
        int v = pair.second;

        auto u_neighbors = warehouse.neighbors(u);
        auto v_neighbors = warehouse.neighbors(v);

        // On filtre les médicaments qui sont connectés à la fois à U et V
        auto common_neighbors = u_neighbors | std::views::filter([&v_neighbors](const auto &neighbor)
                                                                 { return v_neighbors.contains(neighbor.first); }) |
                                std::views::transform([](const auto &neighbor)
                                                      { return std::make_pair(neighbor.first, neighbor.second); }) |
                                std::ranges::to<std::vector>();

        // Tri par distance croissante depuis U
        std::ranges::sort(common_neighbors, [](const auto &a, const auto &b)
                          { return a.second.dist < b.second.dist; });

        Node &node_u = warehouse.get_node(u);
        Node &node_v = warehouse.get_node(v);

        if (!node_u.neighbors.contains(v))
            continue;
        double tot_dist = node_u.neighbors[v].dist;

        // Suppression du lien direct U-V
        node_u.remove_neighbor(node_v);

        double acc_dist = 0.0;
        int last_node_id = u;

        for (auto &neighbor_pair : common_neighbors)
        {
            int nb_id = neighbor_pair.first;
            Node &node_nb = warehouse.get_node(nb_id);

            // On récupère les distances AVANT de supprimer les liens
            double dist_u = node_u.neighbors[nb_id].dist;
            double dist_v = node_v.neighbors[nb_id].dist;
            constexpr double EPS = 1e-6;

            // Scaling si la somme ne correspond pas
            double current_sum = dist_u + dist_v;
            if (std::abs(current_sum - tot_dist) > EPS)
            {
                dist_u *= (tot_dist / current_sum);
            }
            if (dist_u < acc_dist)
                dist_u = acc_dist + 0.001;

            // NETTOYAGE : On casse les liens "en étoile" vers U et V
            node_u.remove_neighbor(node_nb);
            node_v.remove_neighbor(node_nb);

            // CHAÎNAGE : On lie le maillon précédent au nouveau (Bidirectionnel)
            double segment_dist = dist_u - acc_dist;
            warehouse.get_node(last_node_id).add_neighbor(node_nb, segment_dist);

            acc_dist = dist_u;
            last_node_id = nb_id;
        }

        // CONNEXION FINALE : dernier maillon vers V
        warehouse.get_node(last_node_id).add_neighbor(node_v, tot_dist - acc_dist);
    }
    warehouse.export_graph_to_dot("step3.dot");

    // =========================================================================
    // ==== PRECALCUL DE LA MATRICE DE DISTANCE (FIN DU CONSTRUCTEUR)       ====
    // =========================================================================

    int start_node = 0;
    int end_node = 34;

    matrix_nodes.clear();
    matrix_nodes.push_back(start_node);                                                          // Index 0
    matrix_nodes.insert(matrix_nodes.end(), temp_matrix_nodes.begin(), temp_matrix_nodes.end()); // Index 1 à N-2
    matrix_nodes.push_back(end_node);                                                            // Index N-1

    node_to_matrix_index.clear();
    for (size_t i = 0; i < matrix_nodes.size(); ++i)
    {
        node_to_matrix_index[matrix_nodes[i]] = i;
    }

    // Calcul de Dijkstra de tous vers tous pour les noeuds concernés
    distance_matrix = build_distance_matrix(warehouse, matrix_nodes);
}

// ------------------- Évaluation d’un ordre -------------------
double WarehouseEngine::evaluate_order(const std::vector<int> &medicament_ids)
{
    std::vector<int> item_matrix_indices;
    std::unordered_set<int> visited_locations;

    // 1. Traduire les ID de médicaments en Index de Matrice
    for (int med_id : medicament_ids)
    {
        if (medicament_to_location.find(med_id) == medicament_to_location.end())
        {
            throw std::runtime_error("Unknown medicament id: " + std::to_string(med_id));
        }

        int loc_id = medicament_to_location[med_id];
        int node_id = location_to_node.at(loc_id);
        int matrix_index = node_to_matrix_index.at(node_id);

        // On déduplique: si 2 médicaments sont à la même location,
        // on ne visite la location qu'une seule fois.
        // Cela évite l'erreur "Duplicate node detected" de compute_path_cost.
        if (visited_locations.insert(matrix_index).second)
        {
            item_matrix_indices.push_back(matrix_index);
        }
    }

    // 2. Calculer le coût en lecture directe sur la matrice précalculée
    return compute_path_cost(distance_matrix, item_matrix_indices);
}

void WarehouseEngine::load_locations(const std::string &filename)
{
    std::ifstream file(filename);
    if (!file.is_open())
        throw std::runtime_error("Cannot open file: " + filename);

    json j;
    file >> j;

    for (const auto &entry : j)
    {
        Location loc;
        loc.id = entry.at("id").get<int>();
        loc.u = entry.at("u").get<int>();
        loc.v = entry.at("v").get<int>();
        loc.dist_u = entry.at("dist_u").get<double>();
        loc.dist_v = entry.at("dist_v").get<double>();

        location_table[loc.id] = loc;
    }
}

void WarehouseEngine::load_medicament_mapping(const std::string &filename)
{
    std::ifstream file(filename);
    if (!file.is_open())
        throw std::runtime_error("Cannot open file: " + filename);

    json j;
    file >> j;

    for (const auto &entry : j)
    {
        // Si le plantage arrive, on saura exactement sur quel bloc il a échoué
        int medicament_id = entry.at("medicament_id").get<int>();
        int location_id = entry.at("location_id").get<int>();

        if (location_table.find(location_id) == location_table.end())
            throw std::runtime_error("Location id not found for medicament " + std::to_string(medicament_id));

        medicament_to_location[medicament_id] = location_id;
        ++size;
    }
}
void WarehouseEngine::load_files()
{
    std::vector<std::string> potential_paths = {
        "data/",       // Si lancé depuis build/
        "../data/",    // Si lancé depuis python/agents/
        "../../data/", // Si lancé depuis la racine
        "build/data/"};

    std::string base_path = "";
    for (const auto &p : potential_paths)
    {
        if (fs::exists(p + "locations.json"))
        {
            base_path = p;
            break;
        }
    }

    if (base_path.empty())
    {
        throw std::runtime_error("Cannot find data folder. Current path: " + fs::current_path().string());
    }

    load_locations(base_path + "locations.json");
    load_medicament_mapping(base_path + "medicament_locations.json");
}

std::vector<double> WarehouseEngine::get_cumulative_distances(const std::vector<int> &medicament_ids)
{
    std::vector<int> item_indices;
    std::unordered_set<int> visited;
    for (int med_id : medicament_ids)
    {
        int loc_id = medicament_to_location.at(med_id);
        int node_id = location_to_node.at(loc_id);
        int matrix_index = node_to_matrix_index.at(node_id);
        if (visited.insert(matrix_index).second)
        {
            item_indices.push_back(matrix_index);
        }
    }

    std::vector<double> cumulative;
    double current_total = 0.0;
    cumulative.push_back(0.0); // Distance au START

    int start_idx = 0;
    int end_idx = matrix_nodes.size() - 1;

    if (item_indices.empty())
    {
        cumulative.push_back(distance_matrix[start_idx][end_idx]);
        return cumulative;
    }

    // Distance START -> Premier item
    current_total += distance_matrix[start_idx][item_indices[0]];
    cumulative.push_back(current_total);

    // Distances entre items
    for (size_t i = 0; i + 1 < item_indices.size(); ++i)
    {
        current_total += distance_matrix[item_indices[i]][item_indices[i + 1]];
        cumulative.push_back(current_total);
    }

    // Distance item final -> END
    current_total += distance_matrix[item_indices.back()][end_idx];
    cumulative.push_back(current_total);

    return cumulative;
}
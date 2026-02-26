#include "warehouse_engine.hpp"
#include "tsp.hpp"
#include <nlohmann/json.hpp>
#include <fstream>
#include <stdexcept>
#include <iostream>
#include <string_view>
#include <filesystem>
#include <ranges>
#include <algorithm>

using json = nlohmann::json;
namespace fs = std::filesystem;

constexpr char locations_file[] = "data/locations.json";
constexpr char medicament_locations_file[] = "data/medicament_locations.json";

WarehouseEngine::WarehouseEngine()
    : warehouse(buildWarehouseGraph()), size(0)
{
    load_files();
    std::vector<std::pair<int, int>> rangees;
    /*for (auto location_pair : location_table)
    {
        auto location = location_pair.second;
        warehouse.insert_node_between(location.u, location.v, location.dist_u, location.dist_v);
        int u = std::min(location.u, location.v);
        int v = std::max(location.u, location.v);
        if (!std::ranges::contains(rangees, std::pair<int, int>(u, v)))
        {
            rangees.push_back(std::pair<int, int>(u, v));
        }
    }
    for (auto pair : rangees)
    {
        int u = pair.first;
        int v = pair.second;

        auto u_neighbors = warehouse.neighbors(u);
        auto v_neighbors = warehouse.neighbors(v);

        auto common_neighbors = u_neighbors | std::views::filter([&v_neighbors](const auto &neighbor)
                                                                 { return std::ranges::contains(v_neighbors, neighbor); }) |
                                std::ranges::to<std::vector>();

        std::ranges::sort(common_neighbors, [](const auto &a, const auto &b)
                          {
                              return a.dist < b.dist; // Exemple : trier par distance croissante
                          });
    }*/
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
        int medicament_id = entry.at("medicament_id").get<int>();
        int location_id = entry.at("location_id").get<int>();

        if (location_table.find(location_id) == location_table.end())
            throw std::runtime_error("Location id not found for medicament " + std::to_string(medicament_id));

        medicament_to_location[medicament_id] = location_id;
        ++size;
    }
}
double WarehouseEngine::evaluate_order(const std::vector<int> &medicament_ids)
{
    // 1. On utilise une map LOCALE (pas static) pour cette commande précise
    std::unordered_map<int, int> local_inserted_nodes;

    // Structure pour mémoriser les modifications à annuler
    struct UndoInfo
    {
        int node_id;
        int u;
        int v;
        double original_dist;
    };
    std::vector<UndoInfo> history;

    std::vector<int> tsp_nodes;
    int start_node = 0;
    int end_node = 34;
    tsp_nodes.push_back(start_node);

    try
    {
        for (int med_id : medicament_ids)
        {
            if (medicament_to_location.find(med_id) == medicament_to_location.end())
                throw std::runtime_error("Unknown medicament id: " + std::to_string(med_id));

            int loc_id = medicament_to_location[med_id];
            const Location &loc = location_table.at(loc_id);

            int node_number;
            // Si on a déjà inséré ce médicament pour CETTE commande, on réutilise le nœud
            if (local_inserted_nodes.find(loc_id) != local_inserted_nodes.end())
            {
                node_number = local_inserted_nodes[loc_id];
            }
            else
            {
                // Insertion physique dans le graphe
                node_number = warehouse.insert_node_between(loc.u, loc.v, loc.dist_u, loc.dist_v);

                // On stocke les infos pour l'inversion
                history.push_back({node_number, loc.u, loc.v, loc.dist_u + loc.dist_v});
                local_inserted_nodes[loc_id] = node_number;
            }
            tsp_nodes.push_back(node_number);
        }

        tsp_nodes.push_back(end_node);

        // Calcul de la matrice et du coût
        auto matrix = build_distance_matrix(warehouse, tsp_nodes);

        std::vector<int> matrix_item_indices;
        for (size_t i = 1; i < tsp_nodes.size() - 1; ++i)
            matrix_item_indices.push_back(static_cast<int>(i));

        double score = compute_path_cost(matrix, matrix_item_indices);

        // Nettoyage AVANT de retourner le score
        for (auto it = history.rbegin(); it != history.rend(); ++it)
        {
            warehouse.remove_inserted_node(it->node_id, it->u, it->v, it->original_dist);
        }

        return score;
    }
    catch (...)
    {
        // En cas d'exception (ex: Dijkstra qui échoue), on nettoie le graphe quand même
        std::cout << "ERROR" << std::endl;
        for (auto it = history.rbegin(); it != history.rend(); ++it)
        {
            warehouse.remove_inserted_node(it->node_id, it->u, it->v, it->original_dist);
        }
        throw; // Relance l'erreur pour que Python puisse l'attraper
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
        // Optionnel : affiche le dossier actuel pour debugger
        throw std::runtime_error("Cannot find data folder. Current path: " + fs::current_path().string());
    }

    load_locations(base_path + "locations.json");
    load_medicament_mapping(base_path + "medicament_locations.json");
}
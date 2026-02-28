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
#include <cassert>

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
    for (auto &location_pair : location_table)
    {
        auto &location = location_pair.second;
        if (location.u > location.v)
        {
            std::swap(location.u, location.v);
            std::swap(location.dist_u, location.dist_v);
        }

        warehouse.insert_node_between(location.u, location.v, location.dist_u, location.dist_v);

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
        auto common_neighbors = u_neighbors | std::views::filter([&v_neighbors](const auto &n)
                                                                 { return v_neighbors.contains(n.first); }) |
                                std::views::transform([](const auto &n)
                                                      { return std::make_pair(n.first, n.second); }) |
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
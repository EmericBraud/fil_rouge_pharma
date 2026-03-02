#pragma once

#include <unordered_map>
#include <vector>
#include <string>
#include <unordered_set>
#include <queue>
#include "warehouse_graph.hpp"

struct Location
{
    int id;
    int u;
    int v;
    double dist_u;
    double dist_v;
};

class WarehouseEngine
{
public:
    WarehouseEngine();

    void load_locations(const std::string &filename);
    void load_medicament_mapping(const std::string &filename);

    double evaluate_order(const std::vector<int> &medicament_ids);

    int get_size() const
    {
        return size;
    }

    void export_full_path_from_medicaments(
        const std::string &filename,
        const std::vector<int> &medicament_ids) const
    {
        if (medicament_ids.empty())
            return;

        std::vector<int> full_node_path;

        // Fonction pour récupérer le chemin complet entre deux nœuds via Dijkstra + backtracking
        auto get_path_between_nodes = [this](int start_node, int end_node) -> std::vector<int>
        {
            int n = warehouse.size();
            std::vector<double> dist(n, std::numeric_limits<double>::infinity());
            std::vector<int> prev(n, -1);

            dist[start_node] = 0.0;
            using Pair = std::pair<double, int>;
            std::priority_queue<Pair, std::vector<Pair>, std::greater<Pair>> pq;
            pq.push({0.0, start_node});

            while (!pq.empty())
            {
                auto [current_dist, u] = pq.top();
                pq.pop();
                if (current_dist > dist[u])
                    continue;

                for (const auto &[v, edge] : warehouse.neighbors(u))
                {
                    double weight = edge.dist;
                    if (dist[u] + weight < dist[v])
                    {
                        dist[v] = dist[u] + weight;
                        prev[v] = u;
                        pq.push({dist[v], v});
                    }
                }
            }

            // Reconstruction du chemin
            std::vector<int> path;
            for (int at = end_node; at != -1; at = prev[at])
            {
                path.push_back(at);
            }
            std::reverse(path.begin(), path.end());
            return path;
        };

        // Construire le chemin complet
        int last_node = -1;
        for (int med_id : medicament_ids)
        {
            int loc_id = medicament_to_location.at(med_id);
            int node_id = location_to_node.at(loc_id);

            if (last_node == -1)
            {
                full_node_path.push_back(node_id);
            }
            else
            {
                // Récupérer le chemin complet entre le dernier nœud et celui-ci
                std::vector<int> segment = get_path_between_nodes(last_node, node_id);
                // Ajouter tous les nœuds sauf le premier (déjà dans full_node_path)
                full_node_path.insert(full_node_path.end(), segment.begin() + 1, segment.end());
            }
            last_node = node_id;
        }

        // Exporter dans le dot
        warehouse.export_graph_with_path_to_dot(filename, full_node_path);
    }

private:
    WarehouseGraph warehouse;
    int size;

    std::unordered_map<int, Location> location_table;
    std::unordered_map<int, int> medicament_to_location;

    std::unordered_map<int, int> location_to_node;

    std::vector<int> matrix_nodes;
    std::unordered_map<int, int> node_to_matrix_index;
    std::vector<std::vector<double>> distance_matrix;

    void load_files();

    void reset()
    {
        load_files();
        size = 0;
    }
};
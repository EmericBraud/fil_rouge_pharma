#include "graph.hpp"
#include <iostream>
#include <algorithm>
#include <utility>
#include <ranges>
#include <unordered_set>
#include <functional>

WarehouseGraph::WarehouseGraph()
    : nodes_list({}) {}

void WarehouseGraph::add_edge(int u, int v, double dist)
{
    // On s'assure que le vecteur est assez grand pour accueillir u et v
    int max_id = std::max(u, v);
    if (max_id >= static_cast<int>(nodes_list.size()))
    {
        for (int i = nodes_list.size(); i <= max_id; ++i)
        {
            nodes_list.emplace_back(i);
        }
    }

    Node &node_u = nodes_list[u];
    Node &node_v = nodes_list[v];
    node_u.add_neighbor(node_v, dist);
}
void WarehouseGraph::remove_edge(int u, int v)
{
    // On récupère des RÉFÉRENCES aux nœuds pour modifier le graphe réel
    Node &u_node = nodes_list[u];
    Node &v_node = nodes_list[v];

    // Suppression dans le voisinage de u
    std::erase_if(u_node.neighbors, [v](const auto &item)
                  {
        // 'item' est un std::pair<const int, Edge>
        // On vérifie si la destination de l'Edge est v
        return item.second.to == v; });

    // Suppression dans le voisinage de v
    std::erase_if(v_node.neighbors, [u](const auto &item)
                  { return item.second.to == u; });
}

int WarehouseGraph::insert_node_between(
    int u_id, // Utilise l'ID/index directement
    int v_id,
    double dist_u,
    double dist_v)
{
    // 1. Vérification d'existence par index (beaucoup plus rapide que any_of)
    if (u_id < 0 || u_id >= static_cast<int>(nodes_list.size()) || v_id < 0 || v_id >= static_cast<int>(nodes_list.size()))
    {
        throw std::out_of_range("Node index out of bounds");
    }

    // 2. On crée le nouvel ID
    int new_id = nodes_list.size();

    // 3. On ajoute le nœud au vecteur
    nodes_list.emplace_back(new_id);

    // 4. On récupère les références APRÈS le push_back (donc elles sont stables)
    Node &real_u = nodes_list[u_id];
    Node &real_v = nodes_list[v_id];
    Node &new_node = nodes_list.back();

    // 5. On fait les connections (Bidirectionnel pour Dijkstra !)
    real_u.add_neighbor(new_node, dist_u);
    real_v.add_neighbor(new_node, dist_v);

    return new_id;
}

const std::unordered_map<int, Edge> &WarehouseGraph::neighbors(int u) const
{
    return nodes_list[u].neighbors;
}

int WarehouseGraph::size() const
{
    return nodes_list.size();
}

void WarehouseGraph::export_graph_with_path_to_dot(
    const std::string &filename,
    const std::vector<int> &path) const
{
    std::ofstream file(filename);
    file << "graph Warehouse {\n";

    // ==============================
    // 1️⃣  Construire un set des noeuds du chemin
    // ==============================

    std::unordered_set<int> path_nodes(path.begin(), path.end());

    // ==============================
    // 2️⃣  Construire un set des arêtes du chemin
    // ==============================

    std::unordered_set<std::pair<int, int>,
                       std::function<size_t(const std::pair<int, int> &)>>
        path_edges(
            0,
            [](const std::pair<int, int> &p)
            {
                return std::hash<int>()(p.first) ^ std::hash<int>()(p.second);
            });

    for (size_t i = 0; i + 1 < path.size(); ++i)
    {
        int u = std::min(path[i], path[i + 1]);
        int v = std::max(path[i], path[i + 1]);
        path_edges.insert({u, v});
    }

    // ==============================
    // 3️⃣  Écriture des noeuds
    // ==============================

    for (const auto &node : nodes_list)
    {
        if (path_nodes.contains(node.id))
        {
            file << "    " << node.id
                 << " [style=filled, fillcolor=lightcoral];\n";
        }
        else
        {
            file << "    " << node.id << ";\n";
        }
    }

    // ==============================
    // 4️⃣  Écriture des arêtes
    // ==============================

    for (const auto &node : nodes_list)
    {
        for (const auto &[neighbor_id, edge] : node.neighbors)
        {
            if (node.id < neighbor_id) // éviter doublons
            {
                int u = node.id;
                int v = neighbor_id;

                bool is_in_path = path_edges.contains({u, v});

                file << "    " << u << " -- " << v;

                if (is_in_path)
                {
                    file << " [label=\"" << edge.dist
                         << "\", color=red, penwidth=3]";
                }
                else
                {
                    file << " [label=\"" << edge.dist << "\"]";
                }

                file << ";\n";
            }
        }
    }

    file << "}\n";
}
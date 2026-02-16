#include "graph.hpp"
#include <iostream>
#include <algorithm>
#include <utility>
#include <ranges>

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
    node_u.add_neighbor(v, dist);
    node_v.add_neighbor(u, dist);
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
    real_u.add_neighbor(new_id, dist_u);
    real_v.add_neighbor(new_id, dist_v);

    new_node.add_neighbor(u_id, dist_u);
    new_node.add_neighbor(v_id, dist_v);

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
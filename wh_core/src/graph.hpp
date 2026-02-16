#pragma once
#include <vector>

struct Edge
{
    int to;
    double dist;
};

class WarehouseGraph
{
public:
    WarehouseGraph(int num_nodes);

    void add_edge(int u, int v, double dist);
    void remove_edge(int u, int v);
    int insert_node_between(
        int u,
        int v,
        double dist_u,
        double dist_v);

    void remove_inserted_node(int node_id, int u, int v, double original_dist)
    {
        if (node_id >= static_cast<int>(adjacency_list.size()))
            return;

        // 1. Supprimer les arêtes connectées au nœud temporaire
        remove_edge(u, node_id);
        remove_edge(v, node_id);

        // 2. Nettoyer la liste d'adjacence du nœud lui-même
        adjacency_list[node_id].clear();
        // Note: On ne peut pas facilement faire un .pop_back() si d'autres nœuds ont été
        // ajoutés après, donc on vide juste ses connexions.

        // 3. Restaurer l'arête originale
        add_edge(u, v, original_dist);
    }

    const std::vector<Edge> &neighbors(int u) const;

    int size() const;

private:
    std::vector<std::vector<Edge>> adjacency_list;
};
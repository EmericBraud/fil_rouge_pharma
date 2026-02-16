#pragma once
#include <vector>
#include <unordered_map>
#include <ranges>
#include <algorithm>

struct Node;
struct Edge
{
    int to;
    double dist;
    Edge(int _to, double _dist) : to(_to), dist(_dist)
    {
    }
};

struct Node
{
    int id;
    std::unordered_map<int, Edge> neighbors;

    void add_neighbor(int neighbor_id, int dist)
    {
        if (neighbors.contains(neighbor_id))
            return;
        neighbors.insert({neighbor_id, Edge(neighbor_id, dist)});
    }
    void remove_edge(const Node &other)
    {
        if (neighbors.contains(other.id))
        {
            neighbors.erase(other.id);
        }
    }

    bool operator==(int id)
    {
        return id == this->id;
    }

    Node(int _id) : id(_id), neighbors({}) {}
};

class WarehouseGraph
{
public:
    WarehouseGraph();

    void add_edge(int u, int v, double dist);

    void remove_edge(int u, int v);
    void ensure_node_exists(int id)
    {
        if (id >= static_cast<int>(nodes_list.size()))
        {
            for (int i = nodes_list.size(); i <= id; ++i)
            {
                nodes_list.emplace_back(i);
            }
        }
    }

    int insert_node_between(
        int u_id,
        int v_id,
        double dist_u,
        double dist_v);

    void remove_inserted_node(int node_id, int u, int v, double original_dist)
    {
        // On ne supprime pas physiquement le nœud du vecteur pour garder les index stables
        remove_edge(u, node_id);
        remove_edge(v, node_id);

        if (node_id < static_cast<int>(nodes_list.size()))
        {
            nodes_list[node_id].neighbors.clear();
        }

        add_edge(u, v, original_dist);
    }

    const std::unordered_map<int, Edge> &neighbors(int u) const;

    int size() const;

    bool contains(int id_node) const

    {
        return std::ranges::any_of(nodes_list, [id_node](const auto &node)
                                   { return node.id == id_node; });
    }

private:
    std::vector<Node> nodes_list;
};
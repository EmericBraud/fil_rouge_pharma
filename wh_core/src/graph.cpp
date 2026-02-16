#include "graph.hpp"
#include <iostream>
#include <algorithm>

WarehouseGraph::WarehouseGraph(int num_nodes)
    : adjacency_list(num_nodes) {}

void WarehouseGraph::add_edge(int u, int v, double dist)
{
    if (u < 0 || v < 0 ||
        static_cast<size_t>(u) >= adjacency_list.size() ||
        static_cast<size_t>(v) >= adjacency_list.size())
    {
        throw std::out_of_range("Invalid node index");
    }

    adjacency_list[static_cast<size_t>(u)].push_back({v, dist});
    adjacency_list[static_cast<size_t>(v)].push_back({u, dist});
}

void WarehouseGraph::remove_edge(int u, int v)
{
    auto &neighbors_u = adjacency_list[u];
    neighbors_u.erase(
        std::remove_if(neighbors_u.begin(), neighbors_u.end(),
                       [v](const Edge &e)
                       { return e.to == v; }),
        neighbors_u.end());

    auto &neighbors_v = adjacency_list[v];
    neighbors_v.erase(
        std::remove_if(neighbors_v.begin(), neighbors_v.end(),
                       [u](const Edge &e)
                       { return e.to == u; }),
        neighbors_v.end());
}

int WarehouseGraph::insert_node_between(
    int u,
    int v,
    double dist_u,
    double dist_v)
{
    if (u >= size() || v >= size())
    {
        throw std::out_of_range("Invalid node index");
    }

    double original_distance = -1.0;
    bool found = false;

    for (const auto &edge : adjacency_list[u])
    {
        if (edge.to == v)
        {
            original_distance = edge.dist;
            found = true;
            break;
        }
    }

    if (!found)
    {
        throw std::logic_error("No edge exists between the given nodes");
    }

    const double EPS = 1e-6;
    if (std::abs((dist_u + dist_v) - original_distance) > EPS)
    {
        throw std::logic_error("Inserted distances do not match original edge length");
    }

    int new_node = size();
    adjacency_list.push_back(std::vector<Edge>());

    remove_edge(u, v);

    add_edge(new_node, u, dist_u);
    add_edge(new_node, v, dist_v);

    return new_node;
}

const std::vector<Edge> &WarehouseGraph::neighbors(int u) const
{
    return adjacency_list[u];
}

int WarehouseGraph::size() const
{
    return adjacency_list.size();
}
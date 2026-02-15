#pragma once
#include <vector>

struct Edge {
    int to;
    double dist;
};

class WarehouseGraph {
public:
    WarehouseGraph(int num_nodes);

    void add_edge(int u, int v, double dist);
    void remove_edge(int u, int v);
    int insert_node_between(
        int u,
        int v,
        double dist_u,
        double dist_v
    );

    const std::vector<Edge>& neighbors(int u) const;

    int size() const;

private:
    std::vector<std::vector<Edge>> adjacency_list;
};
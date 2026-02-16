#include "dijkstra.hpp"
#include <queue>
#include <limits>

std::vector<double> dijkstra(const WarehouseGraph &g, int start)
{

    int n = g.size();
    std::vector<double> dist(n, std::numeric_limits<double>::infinity());
    dist[start] = 0.0;

    using Pair = std::pair<double, int>;
    std::priority_queue<Pair, std::vector<Pair>, std::greater<Pair>> pq;

    pq.push({0.0, start});

    while (!pq.empty())
    {
        auto [current_dist, u] = pq.top();
        pq.pop();

        if (current_dist > dist[u])
            continue;

        for (const auto &edge_pair : g.neighbors(u))
        {
            auto edge = edge_pair.second;
            int v = edge.to;
            double weight = edge.dist;

            if (dist[u] + weight < dist[v])
            {
                dist[v] = dist[u] + weight;
                pq.push({dist[v], v});
            }
        }
    }

    return dist;
}
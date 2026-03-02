#include "graph.hpp"
#include <iostream>
#include <algorithm>
#include <utility>
#include <ranges>
#include <unordered_set>
#include <functional>
#include <iomanip>
#include <sstream>
#include <cmath>

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
    const std::vector<int> &path,
    const std::unordered_set<int> &medicament_nodes) const
{
    std::ofstream file(filename);
    if (!file.is_open())
        throw std::runtime_error("Impossible d'ouvrir le fichier DOT");

    file << "digraph Warehouse {\n";
    file << "    layout=fdp;\n";
    file << "    K=1.1;\n";
    file << "    overlap=false;\n";
    file << "    sep=\"+10\";\n";
    file << "    splines=true;\n";
    file << "    edge [len=1.2];\n";
    file << "    node [style=\"filled\", fontname=\"Arial\", fontsize=12, penwidth=1.5];\n";

    int N = path.size();

    // =========================
    // Mapping progression chemin
    // =========================
    std::unordered_map<int, double> node_progress;
    for (int i = 0; i < N; ++i)
    {
        if (!node_progress.count(path[i]))
            node_progress[path[i]] = static_cast<double>(i) / (N > 1 ? N - 1 : 1);
    }

    auto hsv_to_hex = [](double h, double s, double v) -> std::string
    {
        double r, g, b;
        int i = floor(h * 6);
        double f = h * 6 - i;
        double p = v * (1 - s);
        double q = v * (1 - f * s);
        double t = v * (1 - (1 - f) * s);

        switch (i % 6)
        {
        case 0:
            r = v;
            g = t;
            b = p;
            break;
        case 1:
            r = q;
            g = v;
            b = p;
            break;
        case 2:
            r = p;
            g = v;
            b = t;
            break;
        case 3:
            r = p;
            g = q;
            b = v;
            break;
        case 4:
            r = t;
            g = p;
            b = v;
            break;
        default:
            r = v;
            g = p;
            b = q;
            break;
        }

        std::stringstream ss;
        ss << "#"
           << std::hex << std::setfill('0')
           << std::setw(2) << (int)(r * 255)
           << std::setw(2) << (int)(g * 255)
           << std::setw(2) << (int)(b * 255);

        return ss.str();
    };

    // =========================
    // NŒUDS
    // =========================
    for (const auto &node : nodes_list)
    {
        std::string shape = medicament_nodes.contains(node.id) ? "box" : "ellipse";
        std::string fillcolor = "#f9f9f9";
        std::string color = "#777777";
        std::string label = std::to_string(node.id);
        double penwidth = 1.0;

        if (node_progress.count(node.id))
        {
            double t = node_progress[node.id];
            fillcolor = hsv_to_hex(t * 0.82, 0.4, 0.98);
            color = "#333333";

            if (!path.empty() && node.id == path.front())
            {
                label = "START\\n" + label;
                color = "#000000";
                penwidth = 4.0;
            }
            else if (!path.empty() && node.id == path.back())
            {
                label = "END\\n" + label;
                color = "#cc0000";
                penwidth = 4.0;
            }
        }

        file << "    " << node.id
             << " [shape=" << shape
             << ", fillcolor=\"" << fillcolor << "\""
             << ", color=\"" << color << "\""
             << ", penwidth=" << penwidth
             << ", label=\"" << label << "\"];\n";
    }

    // =========================
    // ARÊTES
    // =========================
    std::unordered_set<std::string> path_edges_set;

    for (size_t i = 0; i + 1 < path.size(); ++i)
    {
        path_edges_set.insert(
            std::to_string(path[i]) + "->" + std::to_string(path[i + 1]));
    }

    for (const auto &node : nodes_list)
    {
        for (const auto &[neighbor_id, edge] : node.neighbors)
        {
            std::string forward =
                std::to_string(node.id) + "->" + std::to_string(neighbor_id);

            std::string reverse =
                std::to_string(neighbor_id) + "->" + std::to_string(node.id);

            bool is_path_edge =
                path_edges_set.count(forward) ||
                path_edges_set.count(reverse);

            if (path_edges_set.count(forward))
            {
                // Flèche du chemin
                file << "    " << node.id << " -> " << neighbor_id
                     << " [penwidth=2.5, color=\"#222222\", weight=10];\n";
            }
            else if (!is_path_edge && node.id < neighbor_id)
            {
                // Lien structurel UNIQUEMENT si non utilisé par le chemin
                file << "    " << node.id << " -> " << neighbor_id
                     << " [dir=none, color=\"#cccccc\", style=\"dotted\", weight=1];\n";
            }
        }
    }

    file << "}\n";
}
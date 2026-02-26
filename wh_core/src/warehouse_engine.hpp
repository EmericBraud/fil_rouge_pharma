#pragma once

#include <unordered_map>
#include <vector>
#include <string>
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

private:
    WarehouseGraph warehouse;
    int size;

    std::unordered_map<int, Location> location_table;
    std::unordered_map<int, int> medicament_to_location;

    void load_files();

    void reset()
    {
        load_files();
        size = 0;
    }
};
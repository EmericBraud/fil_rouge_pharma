#pragma once

#include <unordered_map>
#include <cstdint>

#include "link.hpp"

enum NODE_DISTANCE_CODE : int
{
    SAME_NODE = 0,
    NO_NODE = -1,
};

struct Node
{
    int id;
    std::unordered_map<int, Link> links;

    bool operator==(const Node &other) const
    {
        return id == other.id;
    }

    int get_distance_from(const Node &other) const
    {
        if (other == *this)
            return NODE_DISTANCE_CODE::SAME_NODE;
        if (!links.contains(other.id))
            return NODE_DISTANCE_CODE::NO_NODE;
        return links[other.id].distance;
    }
};

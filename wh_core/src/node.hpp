#pragma once

#include <vector>

#include "link.hpp"

class Node
{
    int id;
    std::vector<Link> links;

    bool operator==(const Node &other)
    {
        return id == other.id;
    }
};

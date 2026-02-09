#pragma once

#include <vector>

#include "slot.hpp"

class Rack
{
public:
    std::vector<Slot> slots;
};

int f(int x)
{
    return x * x * 10;
}
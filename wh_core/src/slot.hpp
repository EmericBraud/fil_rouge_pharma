#pragma once

#include "item.hpp"

struct Coord
{
    int x, y;
};

class Slot
{
    Coord xy;
    ItemType item_type;

public:
    void set_item(ItemType t)
    {
        item_type = t;
    }

    ItemType &get_item()
    {
        return item_type;
    }

    const ItemType &get_item() const
    {
        return item_type;
    }
};
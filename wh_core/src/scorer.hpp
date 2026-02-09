#pragma once

#include <vector>
#include <cassert>

#include "item.hpp"
#include "rack.hpp"

class Scorer
{
    std::vector<Rack> racks;

public:
    Scorer(int n)
    {
        constexpr int items_per_rack = 10;

        racks.reserve(n / items_per_rack + 1);

        for (int i = 0; i < n; ++i)
        {
            if (i % items_per_rack == 0)
            {
                racks.push_back(Rack());
                racks.back().slots.reserve(items_per_rack);
            }
            Slot new_slot = Slot();
            new_slot.set_item(NONE);
            racks[i / items_per_rack].slots.push_back(new_slot);
        }
    }

    double score(std::vector<ItemType> python_solution)
    {
        {
            // D'abord, on applique la solution proposée
            auto process_n = [](const std::vector<Rack> &racks)
            {
                int n = 0;
                for (const Rack &rack : racks)
                {
                    n += rack.slots.size();
                }
                return n;
            };

            const int n = process_n(racks);

            assert(n == python_solution.size());
        }

        {
            int j = 0;
            for (int i = 0; i < racks.size(); ++i)
                for (int k = 0; k < racks[i].slots.size(); ++k)
                    racks[i].slots[k].set_item(python_solution[j++]);
        }

        // On calcule le score. Pour le moment, c'est n'importe quoi
        int score = 0;
        int j = 0;
        for (const auto &rack : racks)
        {
            for (const auto &slot : rack.slots)
            {
                score += ++j * (static_cast<int>(slot.get_item()) + 1);
            }
        }

        return score;
    }
};
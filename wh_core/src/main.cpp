#include <iostream>
#include "warehouse_engine.hpp"

int main()
{
    std::cout << "Hello, World !" << std::endl;
    WarehouseEngine e;
    std::cout << static_cast<int>(e.evaluate_order({1, 2, 3}));
}
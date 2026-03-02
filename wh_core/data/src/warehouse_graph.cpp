#include "warehouse_graph.hpp"

WarehouseGraph buildWarehouseGraph()
{
    WarehouseGraph g;

    g.add_edge(0, 33, 100.0);
    g.add_edge(0, 35, 150.0);

    g.add_edge(1, 2, 1160.0);
    g.add_edge(1, 3, 110.0);

    g.add_edge(2, 4, 110.0);

    g.add_edge(3, 4, 1160.0);
    g.add_edge(3, 5, 110.0);

    g.add_edge(4, 6, 110.0);

    g.add_edge(5, 6, 1160.0);
    g.add_edge(5, 7, 110.0);

    g.add_edge(6, 8, 110.0);

    g.add_edge(7, 8, 1160.0);
    g.add_edge(7, 10, 620.0);

    g.add_edge(8, 9, 110.0);

    g.add_edge(9, 12, 110.0);

    g.add_edge(10, 11, 110.0);
    g.add_edge(10, 35, 150.0);

    g.add_edge(11, 12, 1890.0);
    g.add_edge(11, 33, 110.0);
    g.add_edge(11, 35, 150.0);

    g.add_edge(12, 13, 110.0);

    g.add_edge(13, 14, 1000.0);
    g.add_edge(13, 15, 189.0);

    g.add_edge(14, 16, 189.0);

    g.add_edge(15, 16, 1000.0);
    g.add_edge(15, 17, 189.0);

    g.add_edge(16, 18, 189.0);

    g.add_edge(17, 18, 1000.0);
    g.add_edge(17, 19, 189.0);

    g.add_edge(18, 20, 189.0);

    g.add_edge(19, 20, 1000.0);
    g.add_edge(19, 21, 189.0);

    g.add_edge(20, 22, 189.0);

    g.add_edge(21, 22, 1000.0);
    g.add_edge(21, 23, 189.0);

    g.add_edge(22, 24, 189.0);

    g.add_edge(23, 24, 1000.0);
    g.add_edge(23, 25, 189.0);

    g.add_edge(24, 26, 189.0);

    g.add_edge(25, 26, 1000.0);
    g.add_edge(25, 27, 189.0);

    g.add_edge(26, 28, 189.0);

    g.add_edge(27, 28, 1000.0);
    g.add_edge(27, 29, 189.0);

    g.add_edge(28, 30, 189.0);

    g.add_edge(29, 30, 1000.0);
    g.add_edge(29, 31, 189.0);

    g.add_edge(30, 32, 189.0);

    g.add_edge(31, 32, 1000.0);
    g.add_edge(31, 33, 189.0);

    g.add_edge(32, 34, 189.0);

    g.add_edge(33, 34, 1000.0);

    return g;
}

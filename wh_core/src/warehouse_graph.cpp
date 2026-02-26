#include "warehouse_graph.hpp"

WarehouseGraph buildWarehouseGraph()
{
    WarehouseGraph g;

    g.add_edge(0, 1, 1160.0);
    g.add_edge(0, 2, 110.0);

    g.add_edge(1, 3, 110.0);

    g.add_edge(2, 3, 1160.0);
    g.add_edge(2, 4, 110.0);

    g.add_edge(3, 5, 110.0);

    g.add_edge(4, 5, 1160.0);
    g.add_edge(4, 7, 110.0);

    g.add_edge(5, 6, 110.0);

    g.add_edge(6, 10, 110.0);

    g.add_edge(7, 8, 620.0);

    g.add_edge(8, 9, 110.0);
    g.add_edge(8, 34, 50.0);

    g.add_edge(9, 11, 1890.0);
    g.add_edge(9, 32, 110.0);
    g.add_edge(9, 34, 50.0);

    g.add_edge(10, 11, 110.0);

    g.add_edge(11, 12, 110.0);

    g.add_edge(12, 13, 1000.0);
    g.add_edge(12, 14, 189.0);

    g.add_edge(13, 15, 189.0);

    g.add_edge(14, 15, 1000.0);
    g.add_edge(14, 16, 189.0);

    g.add_edge(15, 17, 189.0);

    g.add_edge(16, 17, 1000.0);
    g.add_edge(16, 18, 189.0);

    g.add_edge(17, 19, 189.0);

    g.add_edge(18, 19, 1000.0);
    g.add_edge(18, 20, 189.0);

    g.add_edge(19, 21, 189.0);

    g.add_edge(20, 21, 1000.0);
    g.add_edge(20, 22, 189.0);

    g.add_edge(21, 23, 189.0);

    g.add_edge(22, 23, 1000.0);
    g.add_edge(22, 24, 189.0);

    g.add_edge(23, 25, 189.0);

    g.add_edge(24, 25, 1000.0);
    g.add_edge(24, 26, 189.0);

    g.add_edge(25, 27, 189.0);

    g.add_edge(26, 27, 1000.0);
    g.add_edge(26, 28, 189.0);

    g.add_edge(27, 29, 189.0);

    g.add_edge(28, 29, 1000.0);
    g.add_edge(28, 30, 189.0);

    g.add_edge(29, 31, 189.0);

    g.add_edge(30, 31, 1000.0);
    g.add_edge(30, 32, 189.0);

    g.add_edge(31, 33, 189.0);

    g.add_edge(32, 33, 1000.0);
    g.add_edge(32, 34, 160.0);

    return g;
}

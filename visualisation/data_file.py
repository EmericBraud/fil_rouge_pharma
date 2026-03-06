# --- STATIC DATA ---
POS = {
    1: (0, 5),
    2: (0, 2),
    3: (1, 5),
    4: (1, 2),
    5: (2, 5),
    6: (2, 2),
    7: (3, 5),
    8: (3, 2),
    9: (3, -2),
    10: (3, 8),
    35: (3.75, 9.5),
    11: (4.5, 8),
    12: (4.5, -2),
    0: (6, 9.5),
    33: (6, 8),
    31: (6, 7),
    29: (6, 6),
    27: (6, 5),
    25: (6, 4),
    23: (6, 3),
    21: (6, 2),
    19: (6, 1),
    17: (6, 0),
    15: (6, -1),
    13: (6, -2),
    34: (8.5, 8),
    32: (8.5, 7),
    30: (8.5, 6),
    28: (8.5, 5),
    26: (8.5, 4),
    24: (8.5, 3),
    22: (8.5, 2),
    20: (8.5, 1),
    18: (8.5, 0),
    16: (8.5, -1),
    14: (8.5, -2),
}

EDGES = [
    (1, 2),
    (1, 3),
    (3, 4),
    (3, 5),
    (5, 7),
    (7, 8),
    (2, 4),
    (4, 6),
    (6, 8),
    (8, 9),
    (5, 6),
    (7, 10),
    (10, 35),
    (35, 11),
    (11, 12),
    (9, 12),
    (0, 33),
    (11, 33),
    (12, 13),
    (33, 31),
    (31, 29),
    (29, 27),
    (27, 25),
    (25, 23),
    (23, 21),
    (21, 19),
    (19, 17),
    (17, 15),
    (15, 13),
    (34, 32),
    (32, 30),
    (30, 28),
    (28, 26),
    (26, 24),
    (24, 22),
    (22, 20),
    (20, 18),
    (18, 16),
    (16, 14),
    (33, 34),
    (31, 32),
    (29, 30),
    (27, 28),
    (25, 26),
    (23, 24),
    (21, 22),
    (19, 20),
    (17, 18),
    (15, 16),
    (13, 14),
    (0, 35),
    (11, 0),
    (10, 11),
]


def generate_anim_file(meds, order_ids):
    """
    Génère une animation GIF montrant le parcours du pharmacien
    à travers le graphe avec les médicaments ajoutés.

    meds : list of dict
        Liste des médicaments avec {"id", "u", "v", "dist_u", "dist_v"}
    order_ids : list of int
        Ordre de passage des médicaments
    """
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    import tempfile

    # --- Création du graphe et positions ---
    G = nx.Graph()
    G.add_edges_from(EDGES)
    current_pos = POS.copy()  # positions des nodes
    offset = 35  # pour les IDs des nodes "médicaments" dans le graphe
    red_nodes = []

    # --- Ajouter les médicaments comme nodes ---
    for m in meds:
        new_id = m["id"] + offset
        u, v = m["u"], m["v"]
        du, dv = m["dist_u"], m["dist_v"]

        # Position pondérée le long de l'arête
        pu, pv = current_pos[u], current_pos[v]
        new_x = (dv * pu[0] + du * pv[0]) / (du + dv)
        new_y = (dv * pu[1] + du * pv[1]) / (du + dv)
        current_pos[new_id] = (new_x, new_y)
        red_nodes.append(new_id)

        # Modifier le graphe : remplacer l'arête u-v par u-med-v
        G.add_edge(u, new_id)
        G.add_edge(new_id, v)
        if G.has_edge(u, v):
            G.remove_edge(u, v)

    # --- Déterminer le chemin complet ---
    points = [35] + [oid + offset for oid in order_ids] + [0]
    full_path = []
    for i in range(len(points) - 1):
        try:
            path = nx.shortest_path(G, points[i], points[i + 1])
            if i == 0:
                full_path.extend(path)
            else:
                full_path.extend(path[1:])
        except nx.NetworkXNoPath:
            pass

    if not full_path:
        return None

    # --- Création de la figure ---
    fig, ax = plt.subplots(figsize=(6, 8))

    def update(frame):
        ax.clear()
        # Couleur des nodes
        colors = [
            "limegreen" if n in [0, 35] else "red" if n in red_nodes else "lightgray"
            for n in G.nodes()
        ]
        nx.draw(
            G,
            current_pos,
            ax=ax,
            node_color=colors,
            node_size=300,
            with_labels=True,
            font_size=8,
            edge_color="#AAAAAA",
        )

        # Dessiner le chemin parcouru en bleu
        if frame > 0:
            edges_path = list(zip(full_path[: frame + 1], full_path[1 : frame + 1]))
            nx.draw_networkx_edges(
                G,
                current_pos,
                ax=ax,
                edgelist=edges_path,
                edge_color="royalblue",
                width=2,
            )

        # Node courant en orange
        nx.draw_networkx_nodes(
            G,
            current_pos,
            ax=ax,
            nodelist=[full_path[frame]],
            node_color="orange",
            node_shape="p",
            node_size=500,
        )

        ax.axis("off")

    # --- Animation ---
    ani = FuncAnimation(fig, update, frames=len(full_path), interval=300)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
    ani.save(tmp.name, writer="pillow")
    plt.close()
    return tmp.name

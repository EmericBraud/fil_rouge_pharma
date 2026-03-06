import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation
import json


def generer_video_trajet(ordre_passage_json, nom_fichier="trajet_agent.mp4"):
    """
    Prend une liste d'IDs de médicaments et génère une vidéo du trajet.
    """

    # 1. INITIALISATION DU GRAPHE
    G = nx.Graph()

    # Données JSON des médicaments (POI)
    data_json = [
        {"id": 1, "u": 11, "v": 12, "dist_u": 190, "dist_v": 1700},
        {"id": 2, "u": 5, "v": 6, "dist_u": 360, "dist_v": 800},
        {"id": 3, "u": 23, "v": 24, "dist_u": 800, "dist_v": 200},
        {"id": 4, "u": 21, "v": 22, "dist_u": 800, "dist_v": 200},
        {"id": 5, "u": 1, "v": 2, "dist_u": 860, "dist_v": 300},
        {"id": 6, "u": 33, "v": 34, "dist_u": 500, "dist_v": 500},
        {"id": 7, "u": 3, "v": 4, "dist_u": 660, "dist_v": 400},
    ]

    # 2. POSITIONS ET ARÊTES (Statiques)
    pos = {
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

    edges = [
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
    G.add_edges_from(edges)

    # 3. INSERTION POI (Nœuds rouges)
    offset = 35
    red_nodes = []
    for item in data_json:
        new_id = item["id"] + offset
        u, v = item["u"], item["v"]
        du, dv = item["dist_u"], item["dist_v"]
        pu, pv = pos[u], pos[v]
        new_x = (dv * pu[0] + du * pv[0]) / (du + dv)
        new_y = (dv * pu[1] + du * pv[1]) / (du + dv)
        pos[new_id] = (new_x, new_y)
        red_nodes.append(new_id)
        G.add_edge(u, new_id)
        G.add_edge(new_id, v)
        if G.has_edge(u, v):
            G.remove_edge(u, v)

    # 4. CALCUL DE L'ITINÉRAIRE FLUIDE
    # On ajoute l'entrée (35) et la caisse (0)
    points_de_passage = [35] + [i + offset for i in ordre_passage_json] + [0]
    chemin_complet = []
    for i in range(len(points_de_passage) - 1):
        sub_path = nx.shortest_path(G, points_de_passage[i], points_de_passage[i + 1])
        chemin_complet.extend(sub_path if i == 0 else sub_path[1:])

    # 5. DESSIN ET ANIMATION
    node_colors = [
        "limegreen" if n in [0, 35] else "red" if n in red_nodes else "white"
        for n in G.nodes()
    ]

    fig, ax = plt.subplots(figsize=(10, 12))

    def update(frame):
        ax.clear()
        nx.draw(
            G,
            pos,
            ax=ax,
            with_labels=True,
            node_color=node_colors,
            node_size=600,
            edgecolors="black",
            linewidths=1.2,
            font_size=8,
            edge_color="lightgray",
        )

        if frame > 0:
            path_so_far = chemin_complet[: frame + 1]
            edges_so_far = list(zip(path_so_far, path_so_far[1:]))
            nx.draw_networkx_edges(
                G, pos, ax=ax, edgelist=edges_so_far, edge_color="royalblue", width=3
            )

        curr = chemin_complet[frame]
        nx.draw_networkx_nodes(
            G,
            pos,
            ax=ax,
            nodelist=[curr],
            node_shape="p",
            node_size=1000,
            node_color="orange",
        )
        ax.set_title(
            f"Animation Trajet - Étape {frame}/{len(chemin_complet)-1} (Nœud {curr})"
        )
        ax.axis("off")

    ani = FuncAnimation(
        fig, update, frames=len(chemin_complet), interval=400, repeat=False
    )

    # Sauvegarde de la vidéo
    print(f"Génération de la vidéo : {nom_fichier}...")
    try:
        # Essayer d'enregistrer en MP4
        ani.save(nom_fichier, writer="ffmpeg", fps=2)
        print("Vidéo enregistrée avec succès.")
    except Exception as e:
        print(f"Erreur avec ffmpeg : {e}")
        print("Tentative de sauvegarde en GIF...")
        ani.save(nom_fichier.replace(".mp4", ".gif"), writer="pillow", fps=2)

    plt.close()  # Ferme la fenêtre pour éviter l'affichage si on ne veut que le fichier


# --- EXEMPLE D'UTILISATION ---
mon_ordre = [1, 2, 7, 5, 4, 3, 6]
generer_video_trajet(mon_ordre, "mon_parcours_pharmacie.mp4")

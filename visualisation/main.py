import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import streamlit_cytoscape as st_cyto
import tempfile

from data_file import EDGES, POS, generate_anim_file

st.set_page_config(page_title="Pharma Flow Optimizer", layout="wide")
if "medications" not in st.session_state:
    st.session_state.medications = []
if "cytoscape_key" not in st.session_state:
    st.session_state.cytoscape_key = 0


# --- UI ---
st.title("🧪 Pharma Path Interactive Optimizer")
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("📦 Ajouter un Médicament")
    with st.form("add_med"):
        m_id = st.number_input(
            "ID Médicament", min_value=1, value=len(st.session_state.medications) + 1
        )
        edge_choice = st.selectbox(
            "Emplacement (Arête)", [f"{e[0]}-{e[1]}" for e in EDGES]
        )
        u_val, v_val = map(int, edge_choice.split("-"))
        d_u = st.slider("Distance de U", 10, 1000, 500)
        d_v = st.slider("Distance de V", 10, 1000, 500)
        if st.form_submit_button("Ajouter au Graph"):
            st.session_state.medications.append(
                {"id": m_id, "u": u_val, "v": v_val, "dist_u": d_u, "dist_v": d_v}
            )
            st.session_state.cytoscape_key += 1
            st.rerun()

    if st.session_state.medications:
        st.divider()
        st.subheader("📋 Liste")
        for m in st.session_state.medications:
            st.text(f"Med {m['id']} (Arête {m['u']}-{m['v']})")
        if st.button("🗑️ Vider tout"):
            st.session_state.medications = []
            st.session_state.cytoscape_key += 1
            st.rerun()

with col1:
    st.subheader("🗺️ Visualisation Interactive")
    nodes = []

    # Nœuds principaux
    for n in POS:
        is_special = n in [0, 35]
        nodes.append(
            {
                "data": {
                    "id": str(n),
                    "label": str(n),
                    "bg_color": "#32CD32" if is_special else "#FFFFFF",
                    "node_shape": "circle",
                    "node_color": "#000000",
                    "node_width": 35,
                    "node_height": 35,
                    "font_size": 12,
                },
                "position": {"x": POS[n][0] * 80, "y": -POS[n][1] * 80},
                "classes": "special-node" if is_special else "regular-node",
                "selectable": False,
                "grabbable": False,
            }
        )

    # Arêtes principales
    edges = []
    for u, v in EDGES:
        edges.append(
            {
                "data": {"source": str(u), "target": str(v), "id": f"e{u}-{v}"},
                "classes": "regular-edge",
                "selectable": False,
                "grabbable": False,
            }
        )

    # Nœuds médicaments et leurs arêtes
    for m in st.session_state.medications:
        m_node = f"M{m['id']}"
        pu, pv = POS[m["u"]], POS[m["v"]]
        mx = (m["dist_v"] * pu[0] + m["dist_u"] * pv[0]) / (m["dist_u"] + m["dist_v"])
        my = (m["dist_v"] * pu[1] + m["dist_u"] * pv[1]) / (m["dist_u"] + m["dist_v"])

        # Nœud médicament
        nodes.append(
            {
                "data": {"id": m_node, "label": str(m["id"])},
                "position": {"x": mx * 80, "y": -my * 80},
                "classes": "med-node",
                "selectable": False,
                "grabbable": False,
            }
        )

        # Arêtes vers U et V
        edges.append(
            {
                "data": {
                    "source": str(m["u"]),
                    "target": m_node,
                    "id": f"e{m['u']}-{m_node}",
                },
                "classes": "med-edge",
                "selectable": False,
                "grabbable": False,
            }
        )
        edges.append(
            {
                "data": {
                    "source": str(m["v"]),
                    "target": m_node,
                    "id": f"e{m['v']}-{m_node}",
                },
                "classes": "med-edge",
                "selectable": False,
                "grabbable": False,
            }
        )

    # Configuration du layout Cytoscape
    cyto_config = {
        "name": "preset",
        "fit": True,
        "padding": 30,
        "zoom": 1,
        "animate": False,
    }

    # Stylesheet Cytoscape — styles directs sans data(style.xxx)
    stylesheet = [
        # Nœuds normaux (blancs)
        {
            "selector": "node.regular-node",
            "style": {
                "background-color": "#FFFFFF",
                "border-width": 2,
                "border-color": "#000000",
                "width": 35,
                "height": 35,
                "label": "data(label)",
                "text-valign": "center",
                "text-halign": "center",
                "font-size": 12,
                "color": "#000000",
                "shape": "ellipse",
            },
        },
        # Nœuds spéciaux (verts : départ/arrivée)
        {
            "selector": "node.special-node",
            "style": {
                "background-color": "#32CD32",
                "border-width": 2,
                "border-color": "#000000",
                "width": 35,
                "height": 35,
                "label": "data(label)",
                "text-valign": "center",
                "text-halign": "center",
                "font-size": 12,
                "color": "#000000",
                "shape": "ellipse",
            },
        },
        # Nœuds médicaments (rouges, carrés)
        {
            "selector": "node.med-node",
            "style": {
                "background-color": "#FF0000",
                "border-width": 2,
                "border-color": "#000000",
                "width": 25,
                "height": 25,
                "label": "data(label)",
                "text-valign": "center",
                "text-halign": "center",
                "font-size": 10,
                "color": "#FFFFFF",
                "shape": "rectangle",
            },
        },
        # Arêtes normales (grises)
        {
            "selector": "edge.regular-edge",
            "style": {
                "line-color": "#444444",
                "width": 2,
                "curve-style": "bezier",
                "target-arrow-shape": "none",
            },
        },
        # Arêtes médicaments (rouges)
        {
            "selector": "edge.med-edge",
            "style": {
                "line-color": "#FF0000",
                "width": 3,
                "curve-style": "bezier",
                "target-arrow-shape": "none",
            },
        },
    ]

    # Affichage avec une clé unique pour forcer le rafraîchissement
    st_cyto.streamlit_cytoscape(
        elements=nodes + edges,
        layout=cyto_config,
        stylesheet=stylesheet,
        height="600px",
        key=f"graph_view_{st.session_state.cytoscape_key}",
        user_layout=False,
    )

if st.button("🚀 Optimiser & Générer Vidéo"):
    if not st.session_state.medications:
        st.error("Ajoutez au moins un médicament !")
    else:
        with st.spinner("Calcul du trajet..."):
            ordre = [m["id"] for m in st.session_state.medications]
            video_path = generate_anim_file(st.session_state.medications, ordre)
            if video_path:
                st.subheader("📽️ Simulation")
                st.image(video_path)
                with open(video_path, "rb") as f:
                    st.download_button(
                        "💾 Télécharger l'animation", f, "trajet_pharma.gif"
                    )
            else:
                st.error("Erreur lors du calcul du chemin")

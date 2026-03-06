import json
import os
import requests
import streamlit as st
from st_cytoscape import cytoscape

from data_file import EDGES, POS, generate_anim_file

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BUILD_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "build", "data")
LOCATIONS_PATH = os.path.join(BUILD_DATA_DIR, "locations.json")
MEDICAMENT_LOCATIONS_PATH = os.path.join(BUILD_DATA_DIR, "medicament_locations.json")

# À remplacer par le vrai endpoint quand disponible
OPTIMIZE_API_URL = "http://localhost:8000/optimize"

st.set_page_config(page_title="Pharma Flow Optimizer", layout="wide")

if "medications" not in st.session_state:
    st.session_state.medications = []
if "cytoscape_key" not in st.session_state:
    st.session_state.cytoscape_key = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def save_json_files(medications: list) -> None:
    """Sauvegarde locations.json et medicament_locations.json dans ../build/data/"""
    os.makedirs(BUILD_DATA_DIR, exist_ok=True)

    locations = [
        {
            "id": m["id"],
            "u": m["u"],
            "v": m["v"],
            "dist_u": m["dist_u"],
            "dist_v": m["dist_v"],
        }
        for m in medications
    ]

    medicament_locations = [
        {"medicament_id": m["id"], "location_id": m["id"]} for m in medications
    ]

    with open(LOCATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)

    with open(MEDICAMENT_LOCATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(medicament_locations, f, indent=2, ensure_ascii=False)


def call_optimize_api(medications: list) -> list:
    """
    Appelle l'API d'optimisation et retourne l'ordre optimal des IDs médicaments.
    Placeholder : retourne l'ordre d'insertion tant que l'endpoint n'est pas défini.
    Remplace OPTIMIZE_API_URL par le vrai endpoint quand disponible.
    Format attendu en réponse : { "order": [2, 1, 3, ...] }
    """
    payload = {
        "locations": [
            {
                "id": m["id"],
                "u": m["u"],
                "v": m["v"],
                "dist_u": m["dist_u"],
                "dist_v": m["dist_v"],
            }
            for m in medications
        ]
    }

    try:
        response = requests.post(OPTIMIZE_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["order"]  # ex: [3, 1, 2, ...]
    except requests.exceptions.ConnectionError:
        st.warning(
            f"⚠️ API non disponible ({OPTIMIZE_API_URL}). "
            "Utilisation de l'ordre d'insertion par défaut."
        )
        return [m["id"] for m in medications]
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return [m["id"] for m in medications]


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
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
            st.text(
                f"Med {m['id']} — Arête {m['u']}-{m['v']} | U:{m['dist_u']} V:{m['dist_v']}"
            )
        if st.button("🗑️ Vider tout"):
            st.session_state.medications = []
            st.session_state.cytoscape_key += 1
            st.rerun()

# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------
with col1:
    st.subheader("🗺️ Visualisation Interactive")
    elements = []

    # Nœuds principaux
    for n in POS:
        elements.append(
            {
                "data": {"id": str(n), "label": str(n)},
                "position": {"x": POS[n][0] * 80, "y": -POS[n][1] * 80},
                "classes": "special-node" if n in [0, 35] else "regular-node",
                "selectable": False,
                "grabbable": False,
            }
        )

    # Arêtes principales
    for u, v in EDGES:
        elements.append(
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

        elements.append(
            {
                "data": {"id": m_node, "label": str(m["id"])},
                "position": {"x": mx * 80, "y": -my * 80},
                "classes": "med-node",
                "selectable": False,
                "grabbable": False,
            }
        )
        for neighbor in [m["u"], m["v"]]:
            elements.append(
                {
                    "data": {
                        "source": str(neighbor),
                        "target": m_node,
                        "id": f"e{neighbor}-{m_node}",
                    },
                    "classes": "med-edge",
                    "selectable": False,
                    "grabbable": False,
                }
            )

    stylesheet = [
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
        {
            "selector": "edge.regular-edge",
            "style": {
                "line-color": "#444444",
                "width": 2,
                "curve-style": "bezier",
                "target-arrow-shape": "none",
            },
        },
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

    layout = {"name": "preset", "fit": True, "padding": 30, "animate": False}

    cytoscape(
        elements=elements,
        stylesheet=stylesheet,
        layout=layout,
        height="600px",
        user_zooming_enabled=True,
        user_panning_enabled=True,
        key=f"graph_view_{st.session_state.cytoscape_key}",
    )

# ---------------------------------------------------------------------------
# Lancer l'optimisation
# ---------------------------------------------------------------------------
if st.button("🚀 Lancer l'optimisation"):
    if not st.session_state.medications:
        st.error("Ajoutez au moins un médicament !")
    else:
        # 1. Sauvegarde des JSON
        with st.spinner("💾 Sauvegarde des fichiers JSON..."):
            try:
                save_json_files(st.session_state.medications)
                st.success(
                    f"Fichiers sauvegardés :\n"
                    f"- `{LOCATIONS_PATH}`\n"
                    f"- `{MEDICAMENT_LOCATIONS_PATH}`"
                )
            except Exception as e:
                st.error(f"Erreur lors de la sauvegarde : {e}")
                st.stop()

        # 2. Appel API pour l'ordre optimal
        with st.spinner("🔗 Appel API d'optimisation..."):
            ordre_optimal = call_optimize_api(st.session_state.medications)
            st.info(f"Ordre optimal reçu : {ordre_optimal}")

        # 3. Génération de l'animation
        with st.spinner("🎬 Génération de l'animation..."):
            video_path = generate_anim_file(st.session_state.medications, ordre_optimal)
            if video_path:
                st.subheader("📽️ Simulation du trajet optimal")
                st.image(video_path)
                with open(video_path, "rb") as f:
                    st.download_button(
                        "💾 Télécharger l'animation", f, "trajet_pharma.gif"
                    )
            else:
                st.error("Erreur lors de la génération de l'animation.")

import json
import os
import requests
import streamlit as st
import streamlit.components.v1 as components

from pharma3d import render_3d_pharmacy

from data_file import EDGES, POS, generate_anim_file

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BUILD_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "build", "data")
LOCATIONS_PATH = os.path.join(BUILD_DATA_DIR, "locations.json")
MEDICAMENT_LOCATIONS_PATH = os.path.join(BUILD_DATA_DIR, "medicament_locations.json")

OPTIMIZE_API_URL = "http://localhost:8000/optimize"

# Composant custom — Streamlit sert cyto_component/index.html en statique,
# pas besoin de serveur Node.
_COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "cyto_component")
cyto_graph = components.declare_component("cyto_graph", path=_COMPONENT_DIR)

st.set_page_config(page_title="Pharma Flow Optimizer", layout="wide")

if "medications" not in st.session_state:
    st.session_state.medications = []
if "last_result_id" not in st.session_state:
    # Garde trace du dernier médicament ajouté pour éviter les doublons
    # lors des reruns Streamlit
    st.session_state.last_result_id = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def build_elements() -> list:
    elements = []

    for n in POS:
        elements.append(
            {
                "data": {"id": str(n), "label": str(n)},
                "position": {"x": POS[n][0] * 80, "y": -POS[n][1] * 80},
                "classes": "special-node" if n in [0, 35] else "regular-node",
                "grabbable": False,
            }
        )

    for u, v in EDGES:
        elements.append(
            {
                "data": {"source": str(u), "target": str(v), "id": f"e{u}-{v}"},
                "classes": "regular-edge",
                "grabbable": False,
            }
        )

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
                    "grabbable": False,
                }
            )

    return elements


def save_json_files(medications: list) -> None:
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
        return response.json()["order"]
    except requests.exceptions.ConnectionError:
        st.warning(
            f"⚠️ API non disponible ({OPTIMIZE_API_URL}). Ordre par défaut utilisé."
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
    st.subheader("📋 Médicaments ajoutés")
    if not st.session_state.medications:
        st.caption("Aucun médicament — cliquez sur une arête du graphe.")
    else:
        for m in st.session_state.medications:
            st.text(
                f"Med {m['id']} — Arête {m['u']}-{m['v']} | U:{m['dist_u']} V:{m['dist_v']}"
            )
        if st.button("🗑️ Vider tout"):
            st.session_state.medications = []
            st.session_state.last_result_id = None
            st.rerun()

with col1:
    st.subheader("🗺️ Cliquez sur une arête pour y placer un médicament")

    result = cyto_graph(
        elements=build_elements(),
        next_med_id=len(st.session_state.medications) + 1,
        key="cyto_main",
    )

    # result est renvoyé à chaque rerun — on filtre les doublons avec last_result_id
    if result and isinstance(result, dict) and result.get("action") == "add_medication":
        # Clé unique = timestamp envoyé par le JS — insensible aux valeurs identiques
        result_fingerprint = result.get("ts")
        if result_fingerprint != st.session_state.last_result_id:
            st.session_state.last_result_id = result_fingerprint
            st.session_state.medications.append(
                {
                    "id": result["id"],
                    "u": result["u"],
                    "v": result["v"],
                    "dist_u": result["dist_u"],
                    "dist_v": result["dist_v"],
                }
            )
            st.rerun()

# ---------------------------------------------------------------------------
# Lancer l'optimisation
# ---------------------------------------------------------------------------
st.divider()
if st.button("🚀 Lancer l'optimisation", type="primary"):
    if not st.session_state.medications:
        st.error("Ajoutez au moins un médicament !")
    else:
        with st.spinner("💾 Sauvegarde des fichiers JSON..."):
            try:
                save_json_files(st.session_state.medications)
                st.success(
                    f"Fichiers sauvegardés :\n- `{LOCATIONS_PATH}`\n- `{MEDICAMENT_LOCATIONS_PATH}`"
                )
            except Exception as e:
                st.error(f"Erreur lors de la sauvegarde : {e}")
                st.stop()

        with st.spinner("🔗 Appel API d'optimisation..."):
            ordre_optimal = call_optimize_api(st.session_state.medications)
            st.info(f"Ordre optimal reçu : {ordre_optimal}")

        st.subheader("🏥 Simulation 3D du trajet optimal")
        render_3d_pharmacy(st.session_state.medications, ordre_optimal)

        with st.spinner("🎬 Génération du GIF..."):
            video_path = generate_anim_file(st.session_state.medications, ordre_optimal)
            if video_path:
                st.subheader("📽️ Vue 2D — GIF animé")
                st.image(video_path)
                with open(video_path, "rb") as f:
                    st.download_button("💾 Télécharger le GIF", f, "trajet_pharma.gif")
            else:
                st.error("Erreur lors de la génération du GIF.")

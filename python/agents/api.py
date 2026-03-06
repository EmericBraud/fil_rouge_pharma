import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from python.agents.multi_agents import MultiAgentSystem
from python.data import Generator
from python.data.models import Medicament as MedicamentModel

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
N_AGENTS = 10
N_ITER = 120
COLLABORATIF = True
N_POP = 30
P_CROSS = 0.9
P_MUT = 0.2

app = FastAPI(title="Pharma Path Optimizer API")


# ---------------------------------------------------------------------------
# Schémas
# ---------------------------------------------------------------------------
class Location(BaseModel):
    id: int
    u: int
    v: int
    dist_u: int
    dist_v: int


class OptimizeRequest(BaseModel):
    locations: list[Location]


class OptimizeResponse(BaseModel):
    order: list[int]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/optimize", response_model=OptimizeResponse)
def optimize(body: OptimizeRequest):
    if not body.locations:
        raise HTTPException(status_code=400, detail="La liste de locations est vide.")

    try:
        # Remet le compteur d'IDs à zéro avant chaque génération.
        # Sans ça, au 2e appel les IDs générés continuent depuis le 1er appel
        # (ex: 8, 9, 10...) alors que le Scorer attend les IDs du payload.
        MedicamentModel._id_counter = 0

        # Trie par id pour que generate_medicaments(n) produise
        # des IDs 1..n alignés avec les locations triées
        sorted_locations = sorted(body.locations, key=lambda loc: loc.id)
        n = len(sorted_locations)
        medicaments_list = Generator.generate_medicaments(n)

        # Mappe id_location → objet Medicament
        id_to_med = {
            loc.id: med for loc, med in zip(sorted_locations, medicaments_list)
        }

        # Restitue l'ordre original envoyé par le client
        id_order = [loc.id for loc in body.locations]
        medicaments_list = [id_to_med[i] for i in id_order]

        # Optimisation via le système multi-agents
        sma = MultiAgentSystem(
            medicaments=medicaments_list,
            N_agents=N_AGENTS,
            N_pop=N_POP,
            P_cross=P_CROSS,
            P_mut=P_MUT,
            collaboratif=COLLABORATIF,
        )

        final_result, _ = sma.run(num_steps=N_ITER)
        final_ids = [m.id for m in final_result]

        return OptimizeResponse(order=final_ids)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

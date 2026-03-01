from typing import List, Tuple

from mesa import Agent, Model

from python.voisins import VoisinsManager
from python.data.models import Medicament
from python.scoring import Scorer


def trouver_indices_echanges(
    ordre_original: List[Medicament],
    ordre_voisin: List[Medicament],
) -> Tuple[int, int]:
    indices_diff = []

    for idx in range(min(len(ordre_original), len(ordre_voisin))):
        if ordre_original[idx] != ordre_voisin[idx]:
            indices_diff.append(idx)

    if len(indices_diff) == 2:
        return indices_diff[0], indices_diff[1]
    else:
        for i in range(len(ordre_original)):
            for j in range(i + 1, len(ordre_original)):
                test_ordre = list(ordre_original)
                test_ordre[i], test_ordre[j] = test_ordre[j], test_ordre[i]
                if test_ordre == ordre_voisin:
                    return i, j

        return None, None


class TabuSearchAgent(Agent):
    def __init__(
        self,
        model: Model,
        collaboratif: bool,
        tabu_size: int = 30,
        neighborhood_size: int = 30,
    ):
        super().__init__(model)
        self.collaboratif = collaboratif
        self.name = "Tabou"

        self.order = self.model.medicaments

        self.scorer = Scorer()
        self.makespan = self.scorer.score_solution(self.order)

        self.cmax_current = self.makespan
        self.tabu_list = []
        self.tabu_size = tabu_size
        self.neighborhood_size = neighborhood_size

    def run_iteration(self):
        voisinage = []

        for _ in range(self.neighborhood_size):
            ordre_voisin = VoisinsManager.swap_voisin(self.order)

            if ordre_voisin == self.order:
                continue

            cmax_voisin = self.scorer.score_solution(ordre_voisin)

            i, j = trouver_indices_echanges(self.order, ordre_voisin)
            mouvement = (
                tuple(sorted((i, j))) if i is not None and j is not None else None
            )

            voisinage.append((cmax_voisin, ordre_voisin, mouvement))

        if not voisinage:
            return

        voisinage.sort(key=lambda x: x[0])

        best_local_move = None
        best_local_sol = None
        best_local_cmax = float("inf")

        for cmax, sol, mvmt in voisinage:
            is_tabu = mvmt in self.tabu_list
            if (not is_tabu) or (cmax < self.makespan):
                best_local_sol = sol
                best_local_move = mvmt
                best_local_cmax = cmax
                break

        if best_local_sol:
            self.order = best_local_sol
            self.cmax_current = best_local_cmax

            self.tabu_list.append(best_local_move)
            if len(self.tabu_list) > self.tabu_size:
                self.tabu_list.pop(0)

            if self.cmax_current < self.makespan:
                self.makespan = self.cmax_current

    def contact(self):
        best_agent_in_population = None
        best_val = float("inf")

        for a in self.model.agents:
            if a.makespan < best_val:
                best_val = a.makespan
                best_agent_in_population = a

        if (
            best_agent_in_population
            and best_agent_in_population.makespan < self.makespan
        ):
            self.order = list(best_agent_in_population.order)
            self.cmax_current = best_agent_in_population.makespan
            self.makespan = best_agent_in_population.makespan
            self.tabu_list = []

    def step(self):
        self.run_iteration()
        if self.collaboratif:
            self.contact()

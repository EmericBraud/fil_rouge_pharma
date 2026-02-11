import random
import copy
from collections import Counter
from typing import List, Dict, Tuple
from mesa import Agent

from python.scoring import Scorer
from python.data import Medicament
from python.voisins import VoisinsManager


def croiser_individus(
    parent1: List[Medicament], parent2: List[Medicament], frequences: Dict[int, int]
) -> Tuple[List[Medicament], List[Medicament]]:
    n = len(parent1)
    limite_1: int = n // 3
    limite_2: int = (2 * n) // 3

    enfant1 = [
        gene1 if not (limite_1 <= i < limite_2) else gene2
        for i, (gene1, gene2) in enumerate(zip(parent1, parent2))
    ]
    enfant2 = [
        gene2 if not (limite_1 <= i < limite_2) else gene1
        for i, (gene1, gene2) in enumerate(zip(parent1, parent2))
    ]

    def viabiliser(
        enfant1: List[Medicament],
        enfant2: List[Medicament],
    ) -> Tuple[List[Medicament], List[Medicament]]:
        occurences_1 = Counter(enfant1)
        occurences_2 = Counter(enfant2)

        pos_1 = []
        pos_2 = []

        for i in range(n):
            gene1 = enfant1[i]
            gene2 = enfant2[i]

            if occurences_1.get(gene1, 0) > frequences.get(gene1, 0):
                pos_1.append(i)
                occurences_1[gene1] -= 1

            if occurences_2.get(gene2, 0) > frequences.get(gene2, 0):
                pos_2.append(i)
                occurences_2[gene2] -= 1

        for i, j in zip(pos_1, pos_2):
            enfant1[i], enfant2[j] = enfant2[j], enfant1[i]

        return enfant1, enfant2

    return viabiliser(enfant1, enfant2)

def solution_aleatoire(medicaments: List[Medicament]) -> List[Medicament]:
    res = []

    for med in medicaments:
        res.append(med)
        random.shuffle(res)

    return res

def population_aleatoire(medicaments: List[Medicament], N: int) -> List[List[Medicament]]:
    return [solution_aleatoire(medicaments) for _ in range(N)]


class GeneticAgent(Agent):

    def __init__(
        self,
        model,
        N: int,
        P_cross: float,
        P_mut: float,
        collaboratif: bool = False,
    ):
        super().__init__(model=model)
        self.N = N
        self.P_cross = P_cross
        self.P_mut = P_mut
        self.collaboratif = collaboratif

        self.population: List[List[Medicament]] = []
        self.cache: Dict[Tuple[int, ...], float] = {}
        self.frequences: Dict[int, int] = {}
        self.generation = 0

        self.order = self.model.medicaments
        self.population = population_aleatoire(self.order, self.N)
        if self.population:
            self.frequences = Counter(self.population[0])

        self.scorer = Scorer(len(self.model.medicaments))
        self.makespan = self.scorer.score_solution(self.order)
        self._evaluate_population(self.population)

    def _evaluate_population(self, population: List[List[Medicament]]) -> List[float]:
        current_best_cmax = self.makespan
        current_best_individual = self.order
        liste_forces: List[float] = []

        for individu in population:
            F_cmax = self.scorer.score_solution(individu)

            if current_best_cmax > F_cmax:
                current_best_cmax = F_cmax
                current_best_individual = individu

            F = 1 / F_cmax if F_cmax > 0 else float("inf")
            liste_forces.append(F)

        self.makespan = current_best_cmax
        self.order = current_best_individual
        return liste_forces

    def local_search(self):
        # Implémente une génération complète de l'AG
        liste_forces = self._evaluate_population(self.population)
        min_f = min(liste_forces)
        liste_forces_norm = [f - min_f + 0.001 for f in liste_forces]

        parents = random.choices(
            population=self.population, weights=liste_forces_norm, k=self.N
        )
        random.shuffle(parents)

        couples = [[parents[2 * i], parents[2 * i + 1]] for i in range(self.N // 2)]
        P_next = []

        for couple in couples:
            p = random.uniform(0, 1)
            if p < self.P_cross:
                enfant1, enfant2 = croiser_individus(
                    couple[0], couple[1], self.frequences
                )
                P_next.extend([enfant1, enfant2])
            else:
                P_next.extend([copy.deepcopy(couple[0]), copy.deepcopy(couple[1])])

        for i in range(len(P_next)):
            if random.uniform(0, 1) < self.P_mut:
                VoisinsManager.swap_voisin(P_next[i])

        self.population = P_next
        self.generation += 1
        self._evaluate_population(self.population)

    def contact(self):
        best_makespan_global = self.makespan
        best_order_global = self.order

        try:
            agents_list = self.model.agents
        except AttributeError:
            return

        for a in agents_list:
            if a.makespan < best_makespan_global:
                best_makespan_global = a.makespan
                best_order_global = a.order

        if best_makespan_global < self.makespan:
            self.makespan = best_makespan_global
            self.order = best_order_global

            if self.population:
                cmaxes = [
                    self.cache.get(tuple(ind), float("inf")) for ind in self.population
                ]
                if cmaxes:
                    worst_index = cmaxes.index(max(cmaxes))
                    self.population[worst_index] = copy.deepcopy(best_order_global)

    def step(self):
        self.local_search()
        if self.collaboratif:
            self.contact()
            self._evaluate_population(self.population)

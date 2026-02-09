import copy
import random

import numpy as np
from mesa import Agent

from utils.cmax import Cmax_Competences
from utils.generation_voisins import GenerationVoisins


class RecuitSimuleAgent(Agent):

    def __init__(
        self,
        model,
        t0=100,
        alpha=0.95,
        cycle_length=100,
        max_iterations=500,
        collaboratif=False,
    ):
        super().__init__(model)

        self.t0 = t0
        self.alpha = alpha
        self.collaboratif = collaboratif

        self.order = self.generer_ordre()
        self.makespan, _ = Cmax_Competences(self.model.patients, self.order)

        self.temperature = t0
        self.iterations = 0
        self.max_iterations = max_iterations
        self.cycle_iterations = 0
        self.cycle_length = cycle_length

    """
    si je suis collaboratif, j'entre en contact avec les autres
    je vérifie s'il y a mieux que moi, dans ce cas, je recupere le meilleur dans ma population
    """

    def contact(self):
        if not self.collaboratif:
            return

        for agent in self.model.agents:
            if agent != self and agent.makespan < self.makespan:
                self.order = copy.deepcopy(agent.order)
                self.makespan = agent.makespan
                break

    def generer_ordre(self):
        ordre = []
        for idx, patient in enumerate(self.model.patients):
            for idx_ope, operation in enumerate(patient):
                if (
                    idx < len(self.model.patients)
                    and idx_ope < len(patient)
                    and any(comp > 0 for comp in operation)
                ):
                    ordre.append([idx, idx_ope])
        return ordre

    def run_iteration(self):
        if self.iterations >= self.max_iterations:
            return False

        ordre_voisin = GenerationVoisins.generer_voisin(self.order)
        makespan_voisin, _ = Cmax_Competences(self.model.patients, ordre_voisin)

        delta = makespan_voisin - self.makespan

        if delta < 0:
            self.order = ordre_voisin
            self.makespan = makespan_voisin

        else:
            proba = np.exp(-delta / self.temperature)
            if random.random() < proba:
                self.order = ordre_voisin
                self.makespan = makespan_voisin

        self.iterations += 1
        self.cycle_iterations += 1

        if self.cycle_iterations >= self.cycle_length:
            self.temperature = self.alpha * self.temperature
            self.cycle_iterations = 0

        return True

    def step(self):
        still_active = self.run_iteration()

        if self.collaboratif:
            self.contact()

        return still_active

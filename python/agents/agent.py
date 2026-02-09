from mesa import Agent

from python.scoring import scorer


class AgentBase(Agent):
    def __init__(
        self,
        model,
        collaboratif=False,
    ):
        super().__init__(model)

        self.collaboratif = collaboratif

        self.order = self.model.medicaments
        self.makespan = scorer.score_solution(self.order)

    """
    si je suis collaboratif, j'entre en contact avec les autres
    je vérifie s'il y a mieux que moi, dans ce cas, je recupere le meilleur dans ma population
    """

    def contact(self):
        pass

    def step(self):
        pass

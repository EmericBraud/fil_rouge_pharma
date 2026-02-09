from typing import List

from mesa import Model
from mesa.datacollection import DataCollector

from python.agents.recuit_simule import RecuitSimuleAgent
from python.agents.genetic import GeneticAgent
from python.data import Medicament


class MultiAgentSystem(Model):
    def __init__(
        self,
        medicaments: List[Medicament],
        N_agents: int,
        N_pop: int,
        P_cross: float,
        P_mut: float,
        collaboratif: bool,
    ):
        super().__init__()
        self.medicaments = medicaments

        for _ in range(N_agents):
            _ = GeneticAgent(
                model=self,
                N=N_pop,
                P_cross=P_cross,
                P_mut=P_mut,
                collaboratif=collaboratif,
            )
            _ = RecuitSimuleAgent(model=self, collaboratif=collaboratif)

        # DataCollector pour suivre le meilleur makespan global et par agent
        self.datacollector = DataCollector(
            agent_reporters={"Makespan": lambda a: a.makespan},
        )

        self.running = True

    def step(self):
        # Activation aléatoire des agents
        self.datacollector.collect(self)
        self.agents.do("step")
        self.agents.do("advance")

    def run(self, num_steps: int):
        for _ in range(num_steps):
            self.step()

        # Meilleur résultat global
        best_makespan = float("inf")
        best_solution = []
        for agent in self.agents:
            if agent.makespan < best_makespan:
                best_makespan = agent.makespan
                best_solution = agent.order

        return best_solution, best_makespan

    def get_best_makespan(self):
        return (
            min(agent.makespan for agent in self.agents)
            if self.agents
            else float("inf")
        )

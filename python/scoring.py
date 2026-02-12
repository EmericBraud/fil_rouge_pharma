import fil_rouge_py

from python.data import Medicament


class Scorer:
    def __init__(self, n) -> None:
        self.scorer = fil_rouge_py.Scorer(n)

    def score_solution(self, solution: list[Medicament]) -> float:
        return self.scorer.score([medicament.id for medicament in solution])

    def resize(self, n):
        self.scorer.resize(n)


scorer = Scorer(10)

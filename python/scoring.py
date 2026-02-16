import fil_rouge_py

from python.data import Medicament


class Scorer:
    def __init__(self) -> None:
        self.scorer = fil_rouge_py.WarehouseEngine()

    def get_size(self) -> int:
        return self.scorer.get_size()

    def score_solution(self, solution: list[Medicament]) -> float:
        return self.scorer.evaluate_order([medicament.id for medicament in solution])

    def resize(self):
        raise Exception("Object not resizable")

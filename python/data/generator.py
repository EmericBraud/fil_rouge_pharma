from typing import List

from python.data import Medicament


class Generator:
    @staticmethod
    def generate_medicaments(n: int) -> List[Medicament]:
        medicaments = []
        for i in range(n):
            med = Medicament(name=f"medicament_{i+1}")
            medicaments.append(med)
        return medicaments

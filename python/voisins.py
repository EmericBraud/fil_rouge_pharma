import copy
import random
from typing import List

from python.data.models import Medicament


class VoisinsManager:
    @staticmethod
    def est_ordre_valide(ordre: List[Medicament]) -> bool:
        pass

    @staticmethod
    def swap_voisin(ordre: List[Medicament]) -> List[Medicament]:
        """
        Génère un voisin valide en échangeant deux médicaments.
        """
        if len(ordre) <= 1:
            return copy.deepcopy(ordre)

        nouvel_ordre = copy.deepcopy(ordre)

        i, j = random.sample(range(len(nouvel_ordre)), 2)

        med_i = nouvel_ordre[i]
        med_j = nouvel_ordre[j]

        nouvel_ordre[i], nouvel_ordre[j] = med_j, med_i

        # if VoisinsManager.est_ordre_valide(nouvel_ordre):
        return nouvel_ordre

    @staticmethod
    def generer_voisin_insertion(ordre: List[Medicament]) -> List[Medicament]:
        """
        Génère un voisin en déplaçant une opération dans la liste.
        """
        if len(ordre) <= 1:
            return copy.deepcopy(ordre)

        nouvel_ordre = copy.deepcopy(ordre)
        idx_source = random.randint(0, len(nouvel_ordre) - 1)

        positions_valides = []

        for idx_dest in range(len(nouvel_ordre) + 1):
            if idx_dest == idx_source:
                continue

            ordre_temp = nouvel_ordre.copy()
            element = ordre_temp.pop(idx_source)
            ordre_temp.insert(idx_dest, element)

            # if VoisinsManager.est_ordre_valide(ordre_temp):
            positions_valides.append(idx_dest)

        if positions_valides:
            element = nouvel_ordre.pop(idx_source)
            idx_dest_valide = random.choice(positions_valides)
            nouvel_ordre.insert(idx_dest_valide, element)

        return nouvel_ordre

    @staticmethod
    def generer_voisin(ordre: List[Medicament]) -> List[Medicament]:
        """
        Choisit aléatoirement une méthode pour choisir un nouveau voisin
        """
        strategies = [
            VoisinsManager.swap_voisin,
            VoisinsManager.generer_voisin_insertion,
        ]

        for strategie in random.sample(strategies, len(strategies)):
            return strategie(copy.deepcopy(ordre))

        return copy.deepcopy(ordre)

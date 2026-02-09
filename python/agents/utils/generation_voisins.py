import copy
import random
from typing import List


class GenerationVoisins:
    @staticmethod
    def est_ordre_valide(ordre: List[List[int]]) -> bool:
        """
        Vérifie si l'ordre respecte les contraintes de précédence
        """
        dernier_op_par_patient = {}

        for patient, op in ordre:
            if patient in dernier_op_par_patient:
                if not op == dernier_op_par_patient[patient] + 1:
                    return False
            dernier_op_par_patient[patient] = op

        return True

    @staticmethod
    def generer_voisin_valide(ordre: List[List[int]]) -> List[List[int]]:
        """
        Génère un voisin valide en échangeant des opérations de patients différents
        """
        if len(ordre) <= 1:
            return copy.deepcopy(ordre)

        nouvel_ordre = copy.deepcopy(ordre)

        max_tentatives = 100
        for _ in range(max_tentatives):
            i, j = random.sample(range(len(nouvel_ordre)), 2)

            if nouvel_ordre[i][0] != nouvel_ordre[j][0]:
                nouvel_ordre[i], nouvel_ordre[j] = nouvel_ordre[j], nouvel_ordre[i]

                if GenerationVoisins.est_ordre_valide(nouvel_ordre):
                    return nouvel_ordre
                else:
                    nouvel_ordre[i], nouvel_ordre[j] = nouvel_ordre[j], nouvel_ordre[i]

        return copy.deepcopy(ordre)

    @staticmethod
    def generer_voisin_insertion(ordre):
        """
        Génère un voisin en déplaçant une opération
        """
        if len(ordre) <= 1:
            return copy.deepcopy(ordre)

        nouvel_ordre = copy.deepcopy(ordre)

        idx_source = random.randint(0, len(nouvel_ordre) - 1)
        patient_source, op_source = nouvel_ordre[idx_source]

        positions_valides = []

        for idx_dest in range(len(nouvel_ordre) + 1):
            if idx_dest == idx_source:
                continue

            ordre_temp = nouvel_ordre.copy()
            element = ordre_temp.pop(idx_source)
            ordre_temp.insert(idx_dest, element)

            if GenerationVoisins.est_ordre_valide(ordre_temp):
                positions_valides.append(idx_dest)

        if positions_valides:
            element = nouvel_ordre.pop(idx_source)
            idx_dest_valide = random.choice(positions_valides)
            nouvel_ordre.insert(idx_dest_valide, element)

        return nouvel_ordre

    @staticmethod
    def generer_voisin_blocs(ordre):
        """
        Échange des blocs d'opérations de patients différents
        """
        if len(ordre) <= 1:
            return copy.deepcopy(ordre)

        nouvel_ordre = copy.deepcopy(ordre)

        operations_par_patient = {}
        for idx, (patient, op) in enumerate(ordre):
            if patient not in operations_par_patient:
                operations_par_patient[patient] = []
            operations_par_patient[patient].append((idx, op))

        patients = list(operations_par_patient.keys())
        if len(patients) < 2:
            return nouvel_ordre

        patient1, patient2 = random.sample(patients, 2)

        ops_patient1 = operations_par_patient[patient1]
        ops_patient2 = operations_par_patient[patient2]

        if ops_patient1 and ops_patient2:
            idx1, _ = random.choice(ops_patient1)
            idx2, _ = random.choice(ops_patient2)

            nouvel_ordre[idx1], nouvel_ordre[idx2] = (
                nouvel_ordre[idx2],
                nouvel_ordre[idx1],
            )

        return nouvel_ordre

    @staticmethod
    def generer_voisin(ordre):
        """
        Choisit aléatoirement une méthode pour choisir un nouveau voisin
        """
        strategies = [
            GenerationVoisins.generer_voisin_valide,
            GenerationVoisins.generer_voisin_insertion,
            GenerationVoisins.generer_voisin_blocs,
        ]

        for strategie in random.sample(strategies, len(strategies)):
            voisin = strategie(copy.deepcopy(ordre))
            if voisin != ordre and GenerationVoisins.est_ordre_valide(voisin):
                return voisin

        return copy.deepcopy(ordre)

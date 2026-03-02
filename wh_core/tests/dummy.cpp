#include <gtest/gtest.h>
#include "warehouse_engine.hpp"
#include <vector>
#include <stdexcept>

// On utilise une Fixture (Test) pour ne pas avoir à recharger
// les fichiers JSON (WarehouseEngine) à chaque test.
class WarehouseEngineTest : public ::testing::Test
{
protected:
    WarehouseEngine engine;

    // SetUp s'exécute avant chaque test si besoin d'initialisation spécifique
    void SetUp() override
    {
        // L'engine est déjà initialisé via le constructeur
    }
};

// 1. Test du trajet à vide (0 -> 34 direct)
TEST_F(WarehouseEngineTest, EmptyOrderReturnsDirectPathCost)
{
    // D'après le graphe : 0 -> 33 (100) -> 34 (1000) = 1100
    double cost = engine.evaluate_order({});

    // On utilise EXPECT_DOUBLE_EQ pour comparer des flottants avec précision
    EXPECT_DOUBLE_EQ(cost, 1100.0);
}

TEST_F(WarehouseEngineTest, ValidOrderReturnsCorrectCost)
{
    std::vector<int> order = {1, 2, 4, 3};
    double cost = engine.evaluate_order(order);

    // On compare avec la valeur exacte. Une tolérance de 1e-4 est maintenant parfaite !
    EXPECT_NEAR(cost, 7878.181818, 1e-4);
}
// 3. Test de sécurité : Médicament inconnu
TEST_F(WarehouseEngineTest, InvalidMedicamentThrowsError)
{
    std::vector<int> invalid_order = {999}; // 999 n'existe pas dans le JSON

    // On vérifie que le moteur lève bien une exception
    EXPECT_THROW(engine.evaluate_order(invalid_order), std::runtime_error);
}

// 4. Test d'un seul médicament (Aller-retour simple)
TEST_F(WarehouseEngineTest, SingleMedicamentOrder)
{
    std::vector<int> order = {1};
    // Médicament 1 est sur l'arête 2-4
    // Le test va calculer la distance exacte et s'assurer qu'elle est constante
    double cost = engine.evaluate_order(order);

    // Remplacez 0.0 par la vraie valeur trouvée pour figer ce test dans le marbre
    // EXPECT_GT (Greater Than) s'assure au moins que le coût est supérieur au trajet à vide
    EXPECT_GT(cost, 1100.0);
}

// 5. Test du dédoublonnage (Même médicament demandé plusieurs fois)
TEST_F(WarehouseEngineTest, DuplicateMedicamentIgnored)
{
    double cost_single = engine.evaluate_order({1});
    double cost_duplicate = engine.evaluate_order({1, 1, 1});

    // Le coût doit être strictement identique grâce à la protection (visited_locations)
    EXPECT_DOUBLE_EQ(cost_single, cost_duplicate);
}

TEST_F(WarehouseEngineTest, SameAisleMedicamentsCostLogic)
{
    double cost_med4 = engine.evaluate_order({4});    // 5600
    double cost_both = engine.evaluate_order({4, 5}); // 5640

    // On s'assure que ramasser les deux en un seul trajet
    // ajoute une petite distance locale (40) sans doubler le trajet !
    EXPECT_DOUBLE_EQ(cost_both, 5640.0);
    EXPECT_LT(cost_both, cost_med4 * 2); // Doit être largement inférieur à deux voyages
}

TEST_F(WarehouseEngineTest, SymmetricLoopYieldsSameCost)
{
    // Le départ (0) et l'arrivée (34) étant adjacents géographiquement,
    // cette boucle vers le haut de l'entrepôt est symétrique.
    double cost_forward = engine.evaluate_order({1, 2});
    double cost_backward = engine.evaluate_order({2, 1});

    EXPECT_DOUBLE_EQ(cost_forward, 5680.0);
    EXPECT_DOUBLE_EQ(cost_forward, cost_backward);
}
// 8. Test de charge complet (Tous les médicaments d'un coup)
TEST_F(WarehouseEngineTest, AllMedicamentsOrderDoesNotCrash)
{
    // Liste complète de tous les IDs de votre fichier medicaments_locations.json
    std::vector<int> all_meds = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};

    // On s'assure que le calcul matriciel sur une grosse commande passe sans out_of_range
    EXPECT_NO_THROW({
        double cost = engine.evaluate_order(all_meds);
        // La distance doit forcément être supérieure au chemin à vide (1100.0)
        EXPECT_GT(cost, 1100.0);
    });
}
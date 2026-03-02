import matplotlib.pyplot as plt
from python.scoring import Scorer
from python.agents.multi_agents import MultiAgentSystem
from python.data import Generator
from fil_rouge_py import WarehouseEngine

if __name__ == "__main__":
    scorer = Scorer()
    N_MEDICAMENTS = scorer.get_size()
    print(f" [DEBUG] N_MEDICAMENT : {N_MEDICAMENTS}")

    N_AGENTS = 3
    N_ITER = 60
    COLLABORATIF = True
    N_POP = 30
    P_CROSS = 0.9
    P_MUT = 0.2

    # Initialisation du moteur pour l'export
    w = WarehouseEngine()
    medicaments_list = Generator.generate_medicaments(N_MEDICAMENTS)

    # --- Capture de l'état INITIAL ---
    # On prend l'ordre brut généré avant optimisation
    initial_ids = [m.id for m in medicaments_list]
    w.export_path("initial_path.dot", initial_ids)
    print(" [INFO] Graph initial exporté dans 'initial_path.dot'")

    sma = MultiAgentSystem(
        medicaments=medicaments_list,
        N_agents=N_AGENTS,
        N_pop=N_POP,
        P_cross=P_CROSS,
        P_mut=P_MUT,
        collaboratif=COLLABORATIF,
    )

    # Lancement de l'optimisation
    final_result, final_cmax = sma.run(num_steps=N_ITER)

    # --- Capture de l'état FINAL ---
    final_ids = [m.id for m in final_result]
    w.export_path("final_path.dot", final_ids)
    print(" [INFO] Graph final exporté dans 'final_path.dot'")

    print("\n--- Résultat de la Simulation SMA ---")
    print(f"Simulation terminée après {N_ITER} étapes.")
    print(f"Cmax final global: {final_cmax}")

    # --- Affichage du Cmax ---
    agent_data = sma.datacollector.get_agent_vars_dataframe()
    df = agent_data.reset_index()
    df_pivot = df.pivot(index="Step", columns="AgentID", values="Makespan")
    df_pivot.plot(figsize=(10, 6))
    plt.title(f"Évolution du Makespan ({N_ITER} itérations)")
    plt.xlabel("Step")
    plt.ylabel("Makespan")
    plt.grid(True)
    plt.show()

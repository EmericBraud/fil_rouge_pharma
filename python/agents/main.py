import matplotlib.pyplot as plt
from python.scoring import scorer

from python.agents.multi_agents import MultiAgentSystem
from python.data import Generator


if __name__ == "__main__":
    N_MEDICAMENTS = 100
    N_AGENTS = 1
    N_ITER = 80
    COLLABORATIF = True

    scorer.resize(N_MEDICAMENTS)

    sma = MultiAgentSystem(
        medicaments=Generator.generate_medicaments(N_MEDICAMENTS),
        N_agents=N_AGENTS,
        collaboratif=COLLABORATIF,
    )

    final_result, final_cmax = sma.run(num_steps=N_ITER)

    print("\n--- Résultat de la Simulation SMA ---")
    print(f"Simulation terminée après {N_ITER} étapes.")
    print(f"Meilleur ordonnancement global trouvé: {final_result}")
    print(f"Cmax final global: {final_cmax}")

    # --- Affichage du Cmax par agent au fil des itérations ---
    agent_data = sma.datacollector.get_agent_vars_dataframe()
    df = agent_data.reset_index()
    df_pivot = df.pivot(index="Step", columns="AgentID", values="Makespan")
    df_pivot.plot(figsize=(10, 6))
    plt.title("Makespan des agents")
    plt.xlabel("Step")
    plt.ylabel("Makespan")
    plt.show()

import matplotlib.pyplot as plt
from python.scoring import Scorer
from python.agents.multi_agents import MultiAgentSystem
from python.data import Generator
from fil_rouge_py import WarehouseEngine

if __name__ == "__main__":
    scorer = Scorer()
    N_MEDICAMENTS = scorer.get_size()

    print(f"[DEBUG] N_MEDICAMENTS {N_MEDICAMENTS}")

    N_AGENTS = 10
    N_ITER = 200
    COLLABORATIF = True
    N_POP = 30
    P_CROSS = 0.9
    P_MUT = 0.2

    w = WarehouseEngine()
    medicaments_list = Generator.generate_medicaments(N_MEDICAMENTS)

    initial_ids = [m.id for m in medicaments_list]
    w.export_path("initial_path.dot", initial_ids)
    print(f"INITIAL IDs : {initial_ids}")
    dist_initial = w.get_cumulative_distances(initial_ids)

    sma = MultiAgentSystem(
        medicaments=medicaments_list,
        N_agents=N_AGENTS,
        N_pop=N_POP,
        P_cross=P_CROSS,
        P_mut=P_MUT,
        collaboratif=COLLABORATIF,
    )

    final_result, final_cmax = sma.run(num_steps=N_ITER)

    final_ids = [m.id for m in final_result]
    w.export_path("final_path.dot", final_ids)
    dist_final = w.get_cumulative_distances(final_ids)
    print(f"Final IDs : {final_ids}")

    # Création de la figure avec un espacement explicite
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14))
    # Augmente l'espace vertical entre les subplots (0.3 est généralement suffisant)
    plt.subplots_adjust(hspace=0.4)

    # --- Graphique 1 : Évolution SMA ---
    agent_data = sma.datacollector.get_agent_vars_dataframe()
    df = agent_data.reset_index()
    df_pivot = df.pivot(index="Step", columns="AgentID", values="Makespan")

    # On passe explicitement l'axe ax1 à pandas
    df_pivot.plot(ax=ax1)
    ax1.set_title(f"Évolution du Makespan ({N_ITER} itérations)", pad=20)
    ax1.set_xlabel("Itération (Step)")
    ax1.set_ylabel("Makespan (Distance)")
    ax1.grid(True, linestyle="--", alpha=0.7)
    ax1.legend(loc="upper right", fontsize="small", ncol=2)

    # --- Graphique 2 : Distances Cumulées ---
    steps_init = list(range(len(dist_initial)))
    steps_final = list(range(len(dist_final)))

    ax2.plot(
        steps_init,
        dist_initial,
        label=f"Initial (Total: {dist_initial[-1]:.1f})",
        color="gray",
        linestyle="--",
        marker="o",
        markersize=4,
        alpha=0.6,
    )
    ax2.plot(
        steps_final,
        dist_final,
        label=f"Optimisé (Total: {dist_final[-1]:.1f})",
        color="blue",
        linewidth=2,
        marker="s",
        markersize=4,
    )

    ax2.set_title("Comparaison des distances cumulées", pad=20)
    ax2.set_xlabel("Étape du chemin (START -> Items -> END)")
    ax2.set_ylabel("Distance cumulée")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.7)

    # Sauvegarde optionnelle pour vérifier sans chevauchement écran
    # plt.savefig("resultats_simulation.png", bbox_inches='tight')

    plt.show()

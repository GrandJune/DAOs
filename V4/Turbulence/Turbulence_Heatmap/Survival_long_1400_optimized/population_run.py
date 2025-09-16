# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName : autonomy_run.py
# @Software : PyCharm
# Observing PEP 8 coding style

# ---- Set math-library threads BEFORE importing NumPy ----
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import time
import pickle
import numpy as np
import multiprocessing as mp
from Autonomy import Autonomy
from DAO import DAO
from Hierarchy import Hierarchy
from Reality import Reality


def func(m=None, n=None, group_size=None, lr=None, turbulence_freq=None,
         search_loop=None, loop=None):
    """
    One independent replicate. Returns [dao_pct_list, hierarchy_pct_list, autonomy_pct_list].
    """
    rng = np.random.default_rng()        # faster & independent
    reality = Reality(m=m)

    # Local bindings to reduce attribute lookup overhead in hot loops
    AutonomyCls, DAOCls, HierarchyCls = Autonomy, DAO, Hierarchy
    get_payoff = reality.get_payoff
    get_policy_payoff = reality.get_policy_payoff

    # Initial populations
    num_per_type = 50
    autonomy_list  = [AutonomyCls(m=m, n=n, reality=reality, group_size=group_size, lr=lr)
                      for _ in range(num_per_type)]
    dao_list       = [DAOCls(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
                      for _ in range(num_per_type)]
    hierarchy_list = [HierarchyCls(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
                      for _ in range(num_per_type)]

    dao_pct_list, hier_pct_list, auto_pct_list = [], [], []

    # Modulo-free turbulence scheduler
    next_turb = turbulence_freq if (turbulence_freq and turbulence_freq > 0) else None

    for period in range(search_loop):
        # Turbulence event
        if next_turb is not None and period == next_turb:
            reality.change(reality_change_rate=0.2)

            # Payoff refresh (tight loops; keep lookups local)
            for autonomy in autonomy_list:
                for team in autonomy.teams:
                    for ind in team.individuals:
                        ind.payoff = get_payoff(belief=ind.belief)

            for dao in dao_list:
                for team in dao.teams:
                    for ind in team.individuals:
                        ind.payoff = get_payoff(belief=ind.belief)

            for hierarchy in hierarchy_list:
                for team in hierarchy.teams:
                    for ind in team.individuals:
                        ind.payoff = get_payoff(belief=ind.belief)
                superior = hierarchy.superior
                for manager in superior.managers:
                    manager.payoff = get_policy_payoff(policy=manager.policy)
                superior.code_payoff = get_policy_payoff(policy=superior.code)

            # -------- Population replacement (vectorized) --------
            A, D, H = len(autonomy_list), len(dao_list), len(hierarchy_list)

            autonomy_perf = np.fromiter((a.performance_across_time[-1] for a in autonomy_list),
                                        dtype=float, count=A)
            dao_perf      = np.fromiter((d.performance_across_time[-1] for d in dao_list),
                                        dtype=float, count=D)
            hier_perf     = np.fromiter((h.performance_across_time[-1] for h in hierarchy_list),
                                        dtype=float, count=H)

            population = np.concatenate((autonomy_perf, dao_perf, hier_perf), axis=0)
            c = 1.28  # Greve (2002): ~10% expected failure rate
            threshold = population.mean() - c * population.std()

            below_mask = (population < threshold)
            k = int(below_mask.sum())

            # Keep masks per type (avoid O(k) deletions)
            a_slice = slice(0, A)
            d_slice = slice(A, A + D)
            h_slice = slice(A + D, A + D + H)

            keep_a = ~below_mask[a_slice]
            keep_d = ~below_mask[d_slice]
            keep_h = ~below_mask[h_slice]

            if not keep_a.all():
                autonomy_list = [autonomy_list[i] for i in np.flatnonzero(keep_a)]
            if not keep_d.all():
                dao_list      = [dao_list[i]      for i in np.flatnonzero(keep_d)]
            if not keep_h.all():
                hierarchy_list = [hierarchy_list[i] for i in np.flatnonzero(keep_h)]

            # Reseed if everything died
            total = len(autonomy_list) + len(dao_list) + len(hierarchy_list)
            if total == 0:
                autonomy_list.append(AutonomyCls(m=m, n=n, reality=reality, group_size=group_size, lr=lr))
                dao_list.append(DAOCls(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
                hierarchy_list.append(HierarchyCls(m=m, n=n, reality=reality, lr=lr, group_size=group_size))

            # Replacement via multinomial (one draw)
            na, nd, nh = len(autonomy_list), len(dao_list), len(hierarchy_list)
            denom = float(na + nd + nh)
            p_aut, p_dao, p_hie = na / denom, nd / denom, nh / denom

            if k > 0:
                ca, cd, ch = rng.multinomial(k, [p_aut, p_dao, p_hie])
                if ca:
                    autonomy_list.extend(AutonomyCls(m=m, n=n, reality=reality, group_size=group_size, lr=lr)
                                         for _ in range(ca))
                if cd:
                    dao_list.extend(DAOCls(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
                                    for _ in range(cd))
                if ch:
                    hierarchy_list.extend(HierarchyCls(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
                                          for _ in range(ch))

                # Record percentages after replacement
                na2, nd2, nh2 = len(autonomy_list), len(dao_list), len(hierarchy_list)
                denom2 = float(na2 + nd2 + nh2)
                dao_pct_list.append(nd2 / denom2)
                hier_pct_list.append(nh2 / denom2)
                auto_pct_list.append(na2 / denom2)

            # schedule next turbulence
            next_turb += turbulence_freq

        # Core search step (tightened: cached bound calls)
        for a in autonomy_list:
            a.search()
        for d in dao_list:
            d.search(threshold_ratio=0.5)
        for h in hierarchy_list:
            h.search()

    return [dao_pct_list, hier_pct_list, auto_pct_list]


def _slurm_cpus_default():
    try:
        return max(1, int(os.environ.get("SLURM_CPUS_PER_TASK", "1")))
    except ValueError:
        return os.cpu_count() or 1


if __name__ == '__main__':
    t0 = time.time()

    # --- Parameters ---
    m = 90
    turbulence_freq = 100
    group_size = 7
    n = 350
    lr = 0.3
    hyper_repeat = 1
    repetition = 100
    search_loop = 1401

    # --- Parallel settings ---
    WORKERS = _slurm_cpus_default()   # let Slurm control the allocation

    # Prefer 'fork' on Linux; fall back to 'spawn' (e.g., on macOS/Windows)
    try:
        ctx = mp.get_context("fork")
    except ValueError:
        ctx = mp.get_context("spawn")

    dao_percentage_hyper, hierarchy_percentage_hyper, autonomy_percentage_hype = [], [], []

    # One hyper repeat block (kept for structure)
    for _ in range(hyper_repeat):
        with ctx.Pool(processes=WORKERS, maxtasksperchild=25) as pool:
            results = pool.starmap(
                func,
                [(m, n, group_size, lr, turbulence_freq, search_loop, i)
                 for i in range(repetition)]
            )

        # Collect
        dao_percentage_hyper.extend(res[0] for res in results)
        hierarchy_percentage_hyper.extend(res[1] for res in results)
        autonomy_percentage_hype.extend(res[2] for res in results)

    # Average across repetitions (axis=0: time dimension retained)
    dao_percentage        = np.mean(dao_percentage_hyper, axis=0)
    hierarchy_percentage  = np.mean(hierarchy_percentage_hyper, axis=0)
    autonomy_percentage   = np.mean(autonomy_percentage_hype, axis=0)

    # Persist (keep pickle to match your downstream)
    with open("dao_percentage_across_turbulence_time", 'wb') as f:
        pickle.dump(dao_percentage, f)
    with open("hierarchy_percentage_across_turbulence_time", 'wb') as f:
        pickle.dump(hierarchy_percentage, f)
    with open("autonomy_percentage_across_turbulence_time", 'wb') as f:
        pickle.dump(autonomy_percentage, f)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Turbulence Rate=0.2; Frequency=100, Search Loop=1401, Num=50",
          time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))  # Complete time

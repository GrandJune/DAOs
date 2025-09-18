# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: autonomy_run.py
# @Software : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Autonomy import Autonomy
from DAO import DAO
from Hierarchy import Hierarchy
from Reality import Reality
import multiprocessing as mp
import time
import pickle


def func(m=None, n=None, group_size=None, lr=None, turbulence_freq=None,
         search_loop=None, loop=None):
    """
    Worker: runs one repetition and returns only small summaries.
    """
    np.random.seed(None)

    reality = Reality(m=m)
    autonomy_list, dao_list, hierarchy_list = [], [], []
    num_per_type = 40
    for _ in range(num_per_type):
        autonomy_list.append(Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr))
        dao_list.append(DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
        hierarchy_list.append(Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size))

    dao_percentage_list, hierarchy_percentage_list, autonomy_percentage_list = [], [], []

    for period in range(search_loop):
        if period % turbulence_freq == 0:
            reality.change(reality_change_rate=0.2)

            # refresh payoffs after reality change
            for autonomy in autonomy_list:
                for team in autonomy.teams:
                    for individual in team.individuals:
                        individual.payoff = reality.get_payoff(belief=individual.belief)

            for dao in dao_list:
                for team in dao.teams:
                    for individual in team.individuals:
                        individual.payoff = reality.get_payoff(belief=individual.belief)

            for hierarchy in hierarchy_list:
                for team in hierarchy.teams:
                    for individual in team.individuals:
                        individual.payoff = reality.get_payoff(belief=individual.belief)
                # update the manager payoff
                for manager in hierarchy.superior.managers:
                    manager.payoff = reality.get_policy_payoff(policy=manager.policy)
                # update the code payoff
                hierarchy.superior.code_payoff = reality.get_policy_payoff(policy=hierarchy.superior.code)

            # Population replacement
            autonomy_perf = [a.performance_across_time[-1] for a in autonomy_list]
            dao_perf = [d.performance_across_time[-1] for d in dao_list]
            hierarchy_perf = [h.performance_across_time[-1] for h in hierarchy_list]
            population_performance = autonomy_perf + dao_perf + hierarchy_perf
            arr = np.asarray(population_performance, dtype=float)
            # Greve's approach
            # mean_perf = np.mean(population_performance)
            # std_perf = np.std(population_performance)
            #
            # # Threshold (Greve 2002; expected failure rate ≈ 10%)
            # c = 1.28
            # threshold = mean_perf - c * std_perf
            #
            # below_indices = [i for i, perf in enumerate(population_performance) if perf < threshold]

            # Simplified approach
            k = max(1, int(np.ceil(0.10 * arr.size)))  # bottom ~10%, at least 1
            idx = np.argpartition(arr, k - 1)[:k]  # k smallest, unsorted
            # (optional) sort these k by actual value for nicer order
            idx = idx[np.argsort(arr[idx])]
            below_indices = idx.tolist()

            # map global indices to per-type local indices
            A = len(autonomy_list)
            D = len(dao_list)
            # H = len(hierarchy_list)  # not needed explicitly

            autonomy_below, dao_below, hierarchy_below = [], [], []
            for idx in below_indices:
                if idx < A:
                    autonomy_below.append(idx)
                elif idx < A + D:
                    dao_below.append(idx - A)
                else:
                    hierarchy_below.append(idx - A - D)

            # Delete from each list in reverse order to keep indices valid
            for idx in sorted(autonomy_below, reverse=True):
                del autonomy_list[idx]
            for idx in sorted(dao_below, reverse=True):
                del dao_list[idx]
            for idx in sorted(hierarchy_below, reverse=True):
                del hierarchy_list[idx]

            # Replacement
            total = len(autonomy_list) + len(dao_list) + len(hierarchy_list)
            if total == 0:
                autonomy_list.append(Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr))
                dao_list.append(DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
                hierarchy_list.append(Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
                total = 3

            percentage_autonomy = len(autonomy_list) / total
            percentage_dao = len(dao_list) / total
            percentage_hierarchy = len(hierarchy_list) / total

            probs = [percentage_autonomy, percentage_dao, percentage_hierarchy]
            k = len(dao_below) + len(autonomy_below) + len(hierarchy_below)  # number to replace/delete

            if k > 0:
                choices = np.random.choice(["autonomy", "dao", "hierarchy"], size=k, p=probs)
                for choice in choices:
                    if choice == "autonomy":
                        autonomy_list.append(Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr))
                    elif choice == "dao":
                        dao_list.append(DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
                    else:
                        hierarchy_list.append(Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size))

                # record composition after replacement event
                denom = len(autonomy_list) + len(dao_list) + len(hierarchy_list)
                dao_percentage_list.append(len(dao_list) / denom)
                hierarchy_percentage_list.append(len(hierarchy_list) / denom)
                autonomy_percentage_list.append(len(autonomy_list) / denom)

        # Search step each period
        for autonomy in autonomy_list:
            autonomy.search()
        for dao in dao_list:
            dao.search(threshold_ratio=0.5)
        for hierarchy in hierarchy_list:
            hierarchy.search()

    # Return small summaries only (lists of floats). No Manager, no shared memory.
    return loop, dao_percentage_list, hierarchy_percentage_list, autonomy_percentage_list


if __name__ == '__main__':
    t0 = time.time()
    # Parameters
    m = 90
    turbulence_freq = 100
    group_size = 7
    n = 350
    lr = 0.3
    hyper_repeat = 1
    repetition = 100          # hyper * repetition = 1000
    search_loop = 1001

    # Safer default: cap concurrency to avoid memory spikes; adjust if you know your node limits
    concurrency = 100  # set to 100 if you insist, but 16–32 is usually safer

    # DVs
    dao_percentage_hyper, hierarchy_percentage_hyper, autonomy_percentage_hyper = [], [], []

    for _ in range(hyper_repeat):
        results = []

        # Use a Pool to stream results back; maxtasksperchild=1 avoids memory growth in workers
        with mp.Pool(processes=concurrency, maxtasksperchild=1) as pool:
            # callback runs in parent; append immediately (low peak memory)
            def _cb(res):
                results.append(res)

            for loop in range(repetition):
                pool.apply_async(
                    func,
                    (m, n, group_size, lr, turbulence_freq, search_loop, loop),
                    callback=_cb
                )
            pool.close()
            pool.join()

        # results is a list of tuples: (loop, dao_list, hier_list, auto_list)
        # order is not guaranteed; we only need the lists
        for _, dao_l, hier_l, auto_l in results:
            dao_percentage_hyper.append(dao_l)
            hierarchy_percentage_hyper.append(hier_l)
            autonomy_percentage_hyper.append(auto_l)

    # Align lengths if needed (they should be equal across runs given same schedule of turbulence events)
    # Compute means across repetitions (elementwise)
    # Convert to ragged-safe arrays by padding if your events could differ; here we assume equal lengths.
    dao_percentage = np.mean(np.array(dao_percentage_hyper, dtype=float), axis=0)
    hierarchy_percentage = np.mean(np.array(hierarchy_percentage_hyper, dtype=float), axis=0)
    autonomy_percentage = np.mean(np.array(autonomy_percentage_hyper, dtype=float), axis=0)

    # Save the with-time data
    with open("dao_percentage_across_turbulence_time", 'wb') as out_file:
        pickle.dump(dao_percentage, out_file)
    with open("hierarchy_percentage_across_turbulence_time", 'wb') as out_file:
        pickle.dump(hierarchy_percentage, out_file)
    with open("autonomy_percentage_across_turbulence_time", 'wb') as out_file:
        pickle.dump(autonomy_percentage, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Turbulence Rate=0.2; Frequency=200, as per Fang2010",
          time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))  # Complete time

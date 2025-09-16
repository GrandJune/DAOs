# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: autonomy_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Autonomy import Autonomy
from DAO import DAO
from Hierarchy import Hierarchy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle


def func(m=None, n=None, group_size=None, lr=None, turbulence_freq=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    autonomy_list, dao_list, hierarchy_list = [], [], []
    num_per_type = 50
    for _ in range(num_per_type):
        autonomy = Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr)
        dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
        hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size)

        autonomy_list.append(autonomy)
        dao_list.append(dao)
        hierarchy_list.append(hierarchy)

    dao_percentage_list, hierarchy_percentage_list, autonomy_percentage_list = [], [], []
    for period in range(search_loop):
        if period % turbulence_freq == 0 and period != 0:
            reality.change(reality_change_rate=0.2)

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
            # Combine all performances
            autonomy_performance_list = [autonomy.performance_across_time[-1] for autonomy in autonomy_list]
            dao_performance_list = [dao.performance_across_time[-1] for dao in dao_list]
            hierarchy_performance_list = [hierarchy.performance_across_time[-1] for hierarchy in hierarchy_list]
            population_performance = (
                    autonomy_performance_list +
                    dao_performance_list +
                    hierarchy_performance_list
            )
            # Compute population statistics
            mean_perf = np.mean(population_performance)
            std_perf = np.std(population_performance)
            # Threshold
            c = 1.28  # as per Greve 2002, expected  failure rate = 10%
            threshold = mean_perf - c * std_perf

            # Identify indices below threshold
            below_indices = [i for i, perf in enumerate(population_performance) if perf < threshold]

            # IMPORTANT: use *current* lengths to map global indices to per-type local indices
            A = len(autonomy_list)
            D = len(dao_list)
            H = len(hierarchy_list)

            autonomy_below, dao_below, hierarchy_below = [], [], []
            for idx in below_indices:
                if idx < A:
                    autonomy_below.append(idx)  # local index in autonomy_list
                elif idx < A + D:
                    dao_below.append(idx - A)  # local index in dao_list
                else:
                    hierarchy_below.append(idx - A - D)  # local index in hierarchy_list
            # Delete from each list in reverse order to keep indices valid
            for idx in sorted(autonomy_below, reverse=True):
                del autonomy_list[idx]
            for idx in sorted(dao_below, reverse=True):
                del dao_list[idx]
            for idx in sorted(hierarchy_below, reverse=True):
                del hierarchy_list[idx]

            # Replacement
            total = len(autonomy_list) + len(dao_list) + len(hierarchy_list)
            # Edge case: if everything was deleted, re-seed minimally (or skip replacement)
            if total == 0:
                autonomy_list.append(Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr))
                dao_list.append(DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
                hierarchy_list.append(Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
                total = 3

            percentage_autonomy = len(autonomy_list) / total
            percentage_dao = len(dao_list) / total
            percentage_hierarchy = len(hierarchy_list) / total

            # generate types according to percentage
            probs = [
                percentage_autonomy,
                percentage_dao,
                percentage_hierarchy
            ]
            k = len(dao_below) + len(autonomy_below) + len(hierarchy_below)  # number to replace/delete
            if k > 0:
                choices = np.random.choice(
                    ["autonomy", "dao", "hierarchy"],
                    size=k,
                    p=probs
                )
                for choice in choices:
                    if choice == "autonomy":
                        autonomy_list.append(Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr))
                    elif choice == "dao":
                        dao_list.append(DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
                    elif choice == "hierarchy":
                        hierarchy_list.append(Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size))
                dao_percentage_list.append(len(dao_list) / (len(autonomy_list) + len(dao_list) + len(hierarchy_list)))
                hierarchy_percentage_list.append(len(hierarchy_list) / (len(autonomy_list) + len(dao_list) + len(hierarchy_list)))
                autonomy_percentage_list.append(len(autonomy_list) / (len(autonomy_list) + len(dao_list) + len(hierarchy_list)))

        for autonomy in autonomy_list:
            autonomy.search()
        for dao in dao_list:
            dao.search(threshold_ratio=0.5)
        for hierarchy in hierarchy_list:
            hierarchy.search()

    return_dict[loop] = [dao_percentage_list, hierarchy_percentage_list, autonomy_percentage_list]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    turbulence_freq = 200
    group_size = 7
    n = 350
    lr = 0.3
    hyper_repeat = 1
    repetition = 100  # hyper * repetition = 1000
    concurrency = 100
    search_loop = 1001
    # DVs
    dao_percentage_hyper, hierarchy_percentage_hyper, autonomy_percentage_hype = [], [], []
    for _ in range(hyper_repeat):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, n, group_size, lr, turbulence_freq, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.

        dao_percentage_hyper += [result[0] for result in results]
        hierarchy_percentage_hyper += [result[1] for result in results]
        autonomy_percentage_hype += [result[2] for result in results]

    dao_percentage = np.mean(dao_percentage_hyper, axis=0)
    hierarchy_percentage = np.mean(hierarchy_percentage_hyper, axis=0)
    autonomy_percentage = np.mean(autonomy_percentage_hype, axis=0)

    # save the with-time data
    with open("dao_percentage_across_turbulence_time", 'wb') as out_file:
        pickle.dump(dao_percentage, out_file)
    with open("hierarchy_percentage_across_turbulence_time", 'wb') as out_file:
        pickle.dump(hierarchy_percentage, out_file)
    with open("autonomy_percentage_across_turbulence_time", 'wb') as out_file:
        pickle.dump(autonomy_percentage, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Turbulence Rate=0.1; Frequency=200, as per Fang2010", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))  # Complete time

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
    num_per_type = 200
    for _ in range(num_per_type):
        autonomy = Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr)
        dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
        hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
        autonomy_list.append(autonomy)
        dao_list.append(dao)
        hierarchy_list.append(hierarchy)

    for period in range(search_loop):
        if period % turbulence_freq == 0 and period != 0:
            reality.change(reality_change_rate=0.05)

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

        for autonomy in autonomy_list:
            autonomy.search()
        for dao in dao_list:
            dao.search()
        for hierarchy in hierarchy_list:
            hierarchy.search()
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
        c = 1.28  # as per Greve 2002
        threshold = mean_perf - c * std_perf

        # Identify indices below threshold
        below_indices = [i for i, perf in enumerate(population_performance) if perf < threshold]
        autonomy_below = []
        dao_below = []
        hierarchy_below = []
        for idx in below_indices:
            if idx < num_per_type:
                autonomy_below.append(idx)
            elif idx < 2 * num_per_type:
                dao_below.append(idx - num_per_type)  # shift back into dao_list indexing
            else:
                hierarchy_below.append(idx - 2 * num_per_type)  # shift back into hierarchy_list indexing

        # replacement
        percentage_autonomy = len(autonomy_list) / (3 * num_per_type)
        percentage_dao = len(dao_below) / (3 * num_per_type)
        percentage_hierarchy = len(hierarchy_below) / (3 * num_per_type)




    return_dict[loop] = [autonomy.performance_across_time, autonomy.diversity_across_time,
                         autonomy.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    turbulence_freq = 50
    group_size = 7
    n = 350
    lr = 0.3
    hyper_repeat = 10
    repetition = 100  # hyper * repetition = 1000
    concurrency = 100
    search_loop = 1000
    # DVs
    performance_hyper = []
    diversity_hyper = []
    variance_hyper = []
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

        performance_hyper += [result[0] for result in results]
        diversity_hyper += [result[1] for result in results]
        variance_hyper += [result[2] for result in results]

    performance_list = np.mean(performance_hyper, axis=0)
    diversity_list = np.mean(diversity_hyper, axis=0)
    variance_list = np.mean(variance_hyper, axis=0)

    # save the with-time data
    with open("autonomy_performance_across_turbulence_time", 'wb') as out_file:
        pickle.dump(performance_list, out_file)
    with open("autonomy_diversity_across_turbulence_time", 'wb') as out_file:
        pickle.dump(diversity_list, out_file)
    with open("autonomy_variance_across_turbulence_time", 'wb') as out_file:
        pickle.dump(variance_list, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Turbulence Rate=0.1; Frequency=100, as per Fang2010", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))  # Complete time

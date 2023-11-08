# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: hierarchy_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO import DAO
from Hierarchy import Hierarchy
from Autonomy import Autonomy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Pool
from multiprocessing import Semaphore
import pickle
import math


def func(m=None, n=None, group_size=None, lr=None, p1=None, p2=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size, p1=p1, p2=p2)
    for period in range(search_loop):
        if (period + 1) % 50 == 0:
            reality.change(reality_change_rate=0.10)
            # update the individual payoff
            for team in hierarchy.teams:
                for individual in team.individuals:
                    individual.payoff = reality.get_payoff(belief=individual.belief)
            # update the manager payoff
            for manager in hierarchy.superior.managers:
                manager.payoff = reality.get_policy_payoff(policy=manager.policy)
            # update the code payoff
            hierarchy.superior.code_payoff = reality.get_policy_payoff(policy=hierarchy.superior.code)
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_average_across_time,
                         hierarchy.diversity_across_time, hierarchy.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    # turbulence_rate_list = [0.10, 0.12, 0.14, 0.16, 0.18, 0.20]
    group_size = 7
    n = 350
    lr = 0.3
    repetition = 200
    concurrency = 100
    search_loop = 2000
    p1_list = [0.1, 0.2, 0.3, 0.4]
    p2_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    # DVs
    performance_across_p1p2 = []
    superior_performance_across_p1p2 = []
    diversity_across_p1p2 = []
    variance_across_p1p2 = []
    for p1 in p1_list:
        performance_across_p2 = []
        superior_performance_across_p2 = []
        diversity_across_p2 = []
        variance_across_p2 = []
        for p2 in p2_list:
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, p1, p2, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.

            # remove the time dimension, only keep the last value
            performance_across_repeat = [result[0][-1] for result in results]
            superior_performance_across_repeat = [result[1][-1] for result in results]
            diversity_across_repeat = [result[2][-1] for result in results]
            variance_across_repeat = [result[3][-1] for result in results]

            # take an average across repetition, only one value for one parameter
            performance_across_p2.append(sum(performance_across_repeat) / len(performance_across_repeat))
            superior_performance_across_p2.append(
                sum(superior_performance_across_repeat) / len(superior_performance_across_repeat))
            diversity_across_p2.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
            variance_across_p2.append(sum(variance_across_repeat) / len(variance_across_repeat))
        performance_across_p1p2.append(performance_across_p2)
        superior_performance_across_p1p2.append(superior_performance_across_p2)
        diversity_across_p1p2.append(diversity_across_p2)
        variance_across_p1p2.append(variance_across_p2)

        # save the without-time data
        with open("hierarchy_performance_across_p1p2_1", 'wb') as out_file:
            pickle.dump(performance_across_p1p2, out_file)
        with open("superior_performance_across_p1p2_1", 'wb') as out_file:
            pickle.dump(superior_performance_across_p1p2, out_file)
        with open("hierarchy_diversity_across_p1p2_1", 'wb') as out_file:
            pickle.dump(diversity_across_p1p2, out_file)
        with open("hierarchy_variance_across_p1p2_1", 'wb') as out_file:
            pickle.dump(variance_across_p1p2, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
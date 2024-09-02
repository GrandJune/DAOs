# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: hierarchy_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Hierarchy import Hierarchy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle
import os


def func(m=None, n=None, group_size=None, lr=None, p1=None, p2=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size, p1=p1, p2=p2)
    for period in range(search_loop):
        if (period + 1) % 100 == 0:
            reality.change(reality_change_rate=0.15)
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
    return_dict[loop] = [hierarchy.performance_across_time[-1]]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    np.random.seed(None)
    m = 90
    group_size = 7
    n = 350
    lr = 0.3
    repetition = 50
    concurrency = 50
    search_loop = 999

    p1_list = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    p2_list = [0.80]
    # DVs
    performance_across_p1p2 = []
    for p1 in p1_list:  # learning from code
        performance_across_p2 = []
        for p2 in p2_list:  # learning from individuals
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
            performance_across_repeat = [result[0] for result in results]
            performance_across_p2.append(sum(performance_across_repeat) / len(performance_across_repeat))
        performance_across_p1p2.append(performance_across_p2)

    index = 1
    while os.path.exists("hierarchy_performance_8_{0}".format(index)):
        index += 1

    with open("hierarchy_performance_8_{0}".format(index), 'wb') as out_file:
        pickle.dump(performance_across_p1p2, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
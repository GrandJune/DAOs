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


def func(m=None, n=None, group_size=None, lr=None, turbulence_freq=None, turbulence_level=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size, p1=0.1, p2=0.9)
    for period in range(search_loop):
        if (period + 1) % turbulence_freq == 0:
            reality.change(reality_change_rate=turbulence_level)
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
    return_dict[loop] = [hierarchy.performance_across_time[-1], hierarchy.diversity_across_time[-1], turbulence_freq, turbulence_level, lr]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    np.random.seed(None)
    m = 90
    group_size = 7
    n = 350
    repetition = 100
    concurrency = 50
    search_loop = 999

    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        lr = np.random.uniform(0, 1)
        turbulence_freq = np.random.uniform(20, 100)
        turbulence_level = np.random.uniform(0, 0.2)
        sema.acquire()
        p = mp.Process(target=func,
                       args=(m, n, group_size, lr, turbulence_freq, turbulence_level, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.

    index = 1
    while os.path.exists(r"hierarchy_data_{0}".format(index)):
        index += 1

    with open(r"hierarchy_data_{0}".format(index), 'wb') as out_file:
        pickle.dump(results, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
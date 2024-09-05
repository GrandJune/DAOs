# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO import DAO
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
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for period in range(search_loop):
        if (period + 1) % turbulence_freq == 0:
            reality.change(reality_change_rate=turbulence_level)
            for team in dao.teams:
                for individual in team.individuals:
                    individual.payoff = reality.get_payoff(belief=individual.belief)
        dao.search(threshold_ratio=0.5)
    return_dict[loop] = [dao.performance_across_time[-1], dao.performance_across_time[-2], dao.performance_across_time[-3],
                         dao.performance_across_time[-4], dao.performance_across_time[-5],
                         turbulence_freq, turbulence_level, lr]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    np.random.seed(None)
    m = 90
    group_size = 7
    n = 350
    repetition = 80
    concurrency = 40
    search_loop = 1000

    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        lr = np.random.uniform(0, 1)
        turbulence_freq = np.random.choice([20, 40, 60, 80, 100])
        turbulence_level = np.random.choice([0.10, 0.12, 0.14, 0.16, 0.18, 0.20])
        sema.acquire()
        p = mp.Process(target=func,
                       args=(m, n, group_size, lr, turbulence_freq, turbulence_level, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.

    index = 1
    while os.path.exists(r"dao_data_{0}".format(index)):
        index += 1

    with open(r"dao_data_{0}".format(index), 'wb') as out_file:
        pickle.dump(results, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))


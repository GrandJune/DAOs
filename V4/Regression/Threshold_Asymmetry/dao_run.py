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


def func(m=None, n=None, group_size=None, lr=None, asymmetry=None,
         threshold_ratio=None, turbulence_freq=None, turbulence_level=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    mode = 1
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    # pre-assign the token according to the asymmetry degree
    if asymmetry == 0:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = 1
    else:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = (np.random.pareto(a=asymmetry) + 1) * mode

    for period in range(search_loop):
        if (period + 1) % turbulence_freq == 0:
            reality.change(reality_change_rate=turbulence_level)
            for team in dao.teams:
                for individual in team.individuals:
                    individual.payoff = reality.get_payoff(belief=individual.belief)
        dao.search(threshold_ratio=threshold_ratio, token=True)
    return_dict[loop] = [dao.performance_across_time[-1], dao.performance_across_time[-2], dao.performance_across_time[-3],
                         dao.performance_across_time[-4], dao.performance_across_time[-5], asymmetry, threshold_ratio,
                         turbulence_freq, turbulence_level, lr]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    np.random.seed(None)
    m = 90
    n = 350
    lr = 0.3
    repetition = 100
    search_loop = 300
    threshold_ratio_list = np.arange(0.40, 0.71, 0.01)  # 31 cases
    asymmetry_list = [1, 2, 3, 4]
    lr_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    group_size = 7  # the smallest group size in Fang's model: 7

    concurrency = 100
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        asymmetry = np.random.choice(asymmetry_list)
        threshold_ratio = np.random.choice(threshold_ratio_list)
        lr = np.random.choice(lr_list)
        turbulence_freq = np.random.choice([20, 40, 60, 80, 100])
        turbulence_level = np.random.choice([0.10, 0.12, 0.14, 0.16, 0.18, 0.20])
        sema.acquire()
        p = mp.Process(target=func,
                       args=(m, n, group_size, lr, asymmetry, threshold_ratio, turbulence_freq,
                             turbulence_level, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.
    # Automatic integration of results
    time.sleep(np.random.uniform(low=2, high=12))
    if os.path.exists("dao_data"):
        with open("dao_data", 'rb') as infile:
            prior_results = pickle.load(infile)
            results += prior_results
    with open("dao_data", 'wb') as out_file:
        pickle.dump(results, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

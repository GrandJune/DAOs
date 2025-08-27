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


def func(m=None, n=None, group_size=None, lr=None, turbulence_freq=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for period in range(search_loop):
        # if period % turbulence_freq == 0 and period != 0:
        reality.change(reality_change_rate=0.15)
        for team in dao.teams:
            for individual in team.individuals:
                individual.payoff = reality.get_payoff(belief=individual.belief)
        dao.search(threshold_ratio=0.5)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    turbulence_freq = 20
    group_size = 7
    n = 350
    lr = 0.3
    hyper_repeat = 10
    repetition = 100  # hyper * repetition = 1000
    concurrency = 100
    search_loop = 1000
    # DVs
    performance_hyper = []
    consensus_performance_hyper = []
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
        consensus_performance_hyper += [result[1] for result in results]
        diversity_hyper += [result[2] for result in results]
        variance_hyper += [result[3] for result in results]

    performance_list = np.mean(performance_hyper, axis=0)
    consensus_performance_list = np.mean(consensus_performance_hyper, axis=0)
    diversity_list = np.mean(diversity_hyper, axis=0)
    variance_list = np.mean(variance_hyper, axis=0)

    # save the with-time data
    with open("dao_performance_across_turbulence_time", 'wb') as out_file:
        pickle.dump(performance_list, out_file)
    with open("consensus_performance_across_turbulence_time", 'wb') as out_file:
        pickle.dump(consensus_performance_list, out_file)
    with open("dao_diversity_across_turbulence_time", 'wb') as out_file:
        pickle.dump(diversity_list, out_file)
    with open("dao_variance_across_turbulence_time", 'wb') as out_file:
        pickle.dump(variance_list, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Turbulence Rate=0.1; Frequency=100, as per Fang2010", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))  # Complete time

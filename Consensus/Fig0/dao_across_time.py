# -*- coding: utf-8 -*-
# @Time     : 8/5/2022 20:22
# @Author   : Junyi
# @FileName: Exp_s.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Superior import Superior
from Reality import Reality
# import matplotlib
# matplotlib.use('agg')  # For NUS HPC only
# import matplotlib.pyplot as plt
import pickle
import time
import numpy as np
import multiprocessing as mp


def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version="Rushed", loop=None, return_dict=None):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    consensus = [0] * (m // s)
    performance_across_time = []
    for _ in range(search_round):
        for individual in superior.individuals:
            next_index = np.random.choice(len(consensus))
            next_policy = consensus[next_index]
            individual.constrained_local_search_under_consensus(focal_policy=next_policy, focal_policy_index=next_index)
        consensus = []
        for i in range(m//s):
            temp = sum(individual.policy[i] for individual in superior.individuals)
            if temp < 0:
                consensus.append(-1)
            elif temp > 0:
                consensus.append(1)
            else:
                consensus.append(0)
        performance_list = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(performance_list) / len(performance_list))
    return_dict[loop] = performance_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 63  # Christina's paper: 100
    s = 3
    t = 3
    n = 500  # Christina's paper: 280
    search_round = 600
    repetition_round = 100  # Christina's paper
    version = "Rushed"
    authority = False  # Without authority
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition_round):
        p = mp.Process(target=func, args=(m, s, t, authority, n, search_round, version, loop, return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    performance_across_repetition = return_dict.values()

    result_1 = []
    for i in range(search_round):
        temp = [payoff_list[i] for payoff_list in performance_across_repetition]
        result_1.append(sum(temp) / len(temp))
    # Save the original data for further analysis
    with open("dao_performance_across_time", 'wb') as out_file:
        pickle.dump(result_1, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
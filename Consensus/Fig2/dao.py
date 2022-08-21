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
    diversity_across_time = []
    for _ in range(search_round):
        for individual in superior.individuals:
            diversity_across_time.append(superior.get_diversity())
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
    return_dict[loop] = diversity_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 60
    s_list = [1, 2, 3, 4, 5]
    t = 1
    n = 100
    search_round = 500
    repetition_round = 100
    version = "Rushed"
    authority = False  # !!!!!!!!!!!!!!!! Without authority !!!!!!!!!!!!!!!!!!
    data_across_para = []
    for s in s_list:
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition_round):
            p = mp.Process(target=func, args=(m, s, t, authority, n, search_round, version, loop, return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        diversity_across_repetition = return_dict.values()

        result_1 = []
        for i in range(search_round):
            temp = [diversity_list[i] for diversity_list in diversity_across_repetition]
            result_1.append(sum(temp) / len(temp))
        data_across_para.append(result_1)
    # Save the original data for further analysis
    with open("dao_performance_across_s", 'wb') as out_file:
        pickle.dump(data_across_para, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
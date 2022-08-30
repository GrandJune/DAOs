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
from multiprocessing import Pool


def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version="Rushed"):
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
    return performance_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 60  # Christina's paper: 100
    s = 3
    t = 1
    n_list = [10, 50, 100, 150, 200]
    search_round = 600
    repetition_round = 200
    version = "Rushed"
    authority = False  # !!!!!!!!!!!!!!!! Without authority !!!!!!!!!!!!!!!!!!
    data_across_para = []
    for n in n_list:
        cpu_num = mp.cpu_count()
        pool = Pool(cpu_num)
        data_across_repetition = []
        for i in range(repetition_round):
            data_across_repetition.append(
                pool.apply_async(func=func,
                                 args=(
                                     (m, s, t, authority, n, search_round, version))).get())
        result_1 = []
        for i in range(search_round):
            temp = [data_list[i] for data_list in data_across_repetition]
            result_1.append(sum(temp) / len(temp))
        data_across_para.append(result_1)
    # Save the original data for further analysis
    with open("robust_performance_across_n", 'wb') as out_file:
        pickle.dump(data_across_para, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
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


def func(m=None, s=None, n=None, group_size=None, lr=None, asymmetry=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size)
    # pre-assign the token according to the asymmetry degree
    for individual in dao.individuals:
        individual.token = np.random.pareto(a=asymmetry)
    for period in range(search_loop):
        dao.search(threshold_ratio=0.6, enable_token=True)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time, dao.diversity_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 420
    lr = 0.3
    repetition = 400
    search_loop = 1200
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 100
    asymmetry_list = [1, 2, 4, 8]  # smaller asymmetry is associated with higher wealth inequality
    performance_across_para = []
    consensus_across_para = []
    diversity_across_para = []
    for asymmetry in asymmetry_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []

        performance_final = []
        consensus_final = []
        diversity_final = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, s, n, group_size, lr, asymmetry, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_across_repeat = [result[0] for result in results]
        consensus_performance_across_repeat = [result[1] for result in results]
        diversity_across_repeat = [result[2] for result in results]
        for period in range(search_loop):
            performance_temp = [performance_list[period] for performance_list in performance_across_repeat]
            consensus_temp = [consensus_list[period] for consensus_list in consensus_performance_across_repeat]
            diversity_temp = [diversity_list[period] for diversity_list in diversity_across_repeat]
            performance_final.append(performance_temp)
            consensus_final.append(consensus_temp)
            diversity_final.append(diversity_temp)
        performance_across_para.append(performance_final)
        consensus_across_para.append(consensus_final)
        diversity_across_para.append(diversity_final)

    with open("dao_performance", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("dao_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para, out_file)
    with open("dao_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)

    # import matplotlib.pyplot as plt
    # x = range(search_loop)
    # fig, (ax1) = plt.subplots(1, 1)
    # ax1.plot(x, performance_final, "k-", label="DAO")
    # plt.xlabel('Time', fontweight='bold', fontsize=10)
    # plt.ylabel('Performance', fontweight='bold', fontsize=10)
    # # plt.xticks(x)
    # plt.legend(frameon=False, ncol=1, fontsize=10)
    # plt.savefig(r"\DAO_performance.png", transparent=False, dpi=200)
    # t1 = time.time()
    # print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

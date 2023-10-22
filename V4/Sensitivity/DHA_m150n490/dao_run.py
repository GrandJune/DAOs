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


def func(m=None, n=None, group_size=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        dao.search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 150
    n = 490
    lr = 0.3
    threshold_ratio = 0.5
    hyper_iteration = 10
    repetition = 50
    concurrency = 50
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_hyper = []
    consensus_hyper = []
    diversity_hyper = []
    variance_hyper = []
    for hyper_loop in range(hyper_iteration):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, n, group_size, lr, threshold_ratio, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_hyper += [result[0] for result in results]
        consensus_hyper += [result[1] for result in results]
        diversity_hyper += [result[2] for result in results]
        variance_hyper += [result[3] for result in results]

    performance_final = []
    consensus_final = []
    diversity_final = []
    variance_final = []
    percentile_10_final = []
    percentile_90_final = []
    for index in range(search_loop):
        temp_performance = sum([result[index] for result in performance_hyper]) / len(performance_hyper)
        temp_consensus = sum([result[index] for result in consensus_hyper]) / len(consensus_hyper)
        temp_diversity = sum([result[index] for result in diversity_hyper]) / len(diversity_hyper)
        temp_variance = sum([result[index] for result in variance_hyper]) / len(variance_hyper)
        performance_final.append(temp_performance)
        consensus_final.append(temp_consensus)
        diversity_final.append(temp_diversity)
        variance_final.append(temp_variance)

    with open("dao_performance", 'wb') as out_file:
        pickle.dump(performance_final, out_file)
    with open("dao_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_final, out_file)
    with open("dao_diversity", 'wb') as out_file:
        pickle.dump(diversity_final, out_file)
    with open("dao_variance", 'wb') as out_file:
        pickle.dump(variance_final, out_file)

    # save the original data to assess the iteration
    with open("dao_original_performance", 'wb') as out_file:
        pickle.dump(performance_hyper, out_file)
    with open("dao_original_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_hyper, out_file)
    with open("dao_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_hyper, out_file)
    with open("dao_original_variance", 'wb') as out_file:
        pickle.dump(variance_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


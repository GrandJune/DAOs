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


def func(m=None, s=None, n=None, group_size=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        dao.search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time, dao.percentile_10_across_time,
                         dao.percentile_90_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 700
    lr = 0.3
    threshold_ratio = 0.6
    hyper_iteration = 1
    repetition = 50
    concurrency = 50
    search_loop = 1000
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_across_time_hyper = []
    consensus_performance_across_time_hyper = []
    diversity_across_time_hyper = []
    variance_across_time_hyper = []
    percentile_10_across_time_hyper = []
    percentile_90_across_time_hyper = []
    for hyper_loop in range(hyper_iteration):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, s, n, group_size, lr, threshold_ratio, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_across_time = [result[0] for result in results]
        consensus_performance_across_time = [result[1] for result in results]
        diversity_across_time = [result[2] for result in results]
        variance_across_time = [result[3] for result in results]
        percentile_10_across_time = [result[4] for result in results]
        percentile_90_across_time = [result[5] for result in results]
        # for each in performance_across_time:
        #     print(hyper_loop, each[-1])
        # emerge the hyper_loop
        performance_across_time_hyper += performance_across_time
        consensus_performance_across_time_hyper += consensus_performance_across_time
        diversity_across_time_hyper += diversity_across_time
        variance_across_time_hyper += variance_across_time
        percentile_10_across_time_hyper += percentile_10_across_time
        percentile_90_across_time_hyper += percentile_90_across_time


    performance_across_time_final = []
    consensus_performance_across_time_final = []
    diversity_across_time_final = []
    variance_across_time_final = []
    percentile_10_across_time_final = []
    percentile_90_across_time_final = []
    for index in range(search_loop):
        temp_performance = sum([result[index] for result in performance_across_time_hyper]) / len(performance_across_time_hyper)
        temp_consensus = sum([result[index] for result in consensus_performance_across_time_hyper]) / len(consensus_performance_across_time_hyper)
        temp_diversity = sum([result[index] for result in diversity_across_time_hyper]) / len(diversity_across_time_hyper)
        temp_variance = sum([result[index] for result in variance_across_time_hyper]) / len(variance_across_time_hyper)
        temp_percentile_10 = sum([result[index] for result in percentile_10_across_time_hyper]) / len(percentile_10_across_time_hyper)
        temp_percentile_90 = sum([result[index] for result in percentile_90_across_time_hyper]) / len(percentile_90_across_time_hyper)
        performance_across_time_final.append(temp_performance)
        consensus_performance_across_time_final.append(temp_consensus)
        diversity_across_time_final.append(temp_diversity)
        variance_across_time_final.append(temp_variance)
        percentile_10_across_time_final.append(temp_percentile_10)
        percentile_90_across_time_final.append(temp_percentile_90)

    with open("dao_performance_across_time", 'wb') as out_file:
        pickle.dump(performance_across_time_final, out_file)
    with open("dao_consensus_performance_across_time", 'wb') as out_file:
        pickle.dump(consensus_performance_across_time_final, out_file)
    with open("dao_diversity_across_time", 'wb') as out_file:
        pickle.dump(diversity_across_time_final, out_file)
    with open("dao_variance_across_time", 'wb') as out_file:
        pickle.dump(variance_across_time_final, out_file)
    with open("dao_percentile_10_across_time", 'wb') as out_file:
        pickle.dump(percentile_10_across_time_final, out_file)
    with open("dao_percentile_90_across_time", 'wb') as out_file:
        pickle.dump(percentile_90_across_time_final, out_file)

    # save the original data to assess the iteration
    with open("dao_original_performance", 'wb') as out_file:
        pickle.dump(performance_across_time_hyper, out_file)
    with open("dao_original_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_performance_across_time_hyper, out_file)
    with open("dao_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_time_hyper, out_file)
    with open("dao_original_variance", 'wb') as out_file:
        pickle.dump(variance_across_time_hyper, out_file)
    with open("dao_original_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_across_time_hyper, out_file)
    with open("dao_original_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_across_time_hyper, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


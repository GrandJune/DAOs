# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: hierarchy_run.py
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


def func(m=None, s=None, n=None, group_size=None, lr=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    hierarchy = Hierarchy(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_average_across_time,
                         hierarchy.diversity_across_time, hierarchy.variance_across_time,
                         hierarchy.percentile_10_across_time, hierarchy.percentile_90_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 350
    lr = 0.3
    hyper_iteration = 4
    repetition = 50
    concurrency = 50
    search_loop = 100
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_across_time_hyper = []
    superior_performance_across_time_hyper = []
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
            p = mp.Process(target=func, args=(m, s, n, group_size, lr, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        # emerge the hyper_loop
        performance_across_time_hyper.append([result[0] for result in results])
        superior_performance_across_time_hyper.append([result[1] for result in results])
        diversity_across_time_hyper.append([result[2] for result in results])
        variance_across_time_hyper.append([result[3] for result in results])
        percentile_10_across_time_hyper.append([result[4] for result in results])
        percentile_90_across_time_hyper.append([result[5] for result in results])

    performance_across_time_final = []
    superior_performance_across_time_final = []
    diversity_across_time_final = []
    variance_across_time_final = []
    percentile_10_across_time_final = []
    percentile_90_across_time_final = []
    for index in range(search_loop):
        temp_performance = sum([result[index] for result in performance_across_time_hyper]) / len(performance_across_time_hyper)
        temp_superior = sum([result[index] for result in superior_performance_across_time_hyper]) / len(superior_performance_across_time_hyper)
        temp_diveristy = sum([result[index] for result in diversity_across_time_hyper]) / len(diversity_across_time_hyper)
        temp_variance = sum([result[index] for result in variance_across_time_hyper]) / len(variance_across_time_hyper)
        temp_percentile_10 = sum([result[index] for result in percentile_10_across_time_hyper]) / len(percentile_10_across_time_hyper)
        temp_percentile_90 = sum([result[index] for result in percentile_90_across_time_hyper]) / len(percentile_90_across_time_hyper)

        performance_across_time_final.append(temp_performance)
        superior_performance_across_time_final.append(temp_superior)
        diversity_across_time_final.append(temp_diveristy)
        variance_across_time_final.append(temp_variance)
        percentile_10_across_time_final.append(temp_percentile_10)
        percentile_90_across_time_final.append(temp_percentile_90)

    with open("hierarchy_performance_across_time", 'wb') as out_file:
        pickle.dump(performance_across_time_final, out_file)
    with open("hierarchy_superior_performance_across_time", 'wb') as out_file:
        pickle.dump(superior_performance_across_time_final, out_file)
    with open("hierarchy_diversity_across_time", 'wb') as out_file:
        pickle.dump(diversity_across_time_final, out_file)
    with open("hierarchy_variance_across_time", 'wb') as out_file:
        pickle.dump(variance_across_time_final, out_file)
    with open("hierarchy_percentile_10_across_time", 'wb') as out_file:
        pickle.dump(percentile_10_across_time_final, out_file)
    with open("hierarchy_percentile_90_across_time", 'wb') as out_file:
        pickle.dump(percentile_90_across_time_final, out_file)

    # save the original data to assess the iteration
    with open("hierarchy_original_performance", 'wb') as out_file:
        pickle.dump(performance_across_time_hyper, out_file)
    with open("hierarchy_original_superior_performance", 'wb') as out_file:
        pickle.dump(superior_performance_across_time_hyper, out_file)
    with open("hierarchy_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_time_hyper, out_file)
    with open("hierarchy_original_variance", 'wb') as out_file:
        pickle.dump(variance_across_time_hyper, out_file)
    with open("hierarchy_original_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_across_time_hyper, out_file)
    with open("hierarchy_original_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_across_time_hyper, out_file)


    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))





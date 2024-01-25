# -*- coding: utf-8 -*-
# @Time     : 24/01/2024 19:05
# @Author   : Junyi
# @FileName: hierarchy_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Hierarchy import Hierarchy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle


def func(m=None, n=None, group_size=None, lr=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_average_across_time,
                         hierarchy.diversity_across_time, hierarchy.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    hyper_iteration = 5
    repetition = 100
    concurrency = 100
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_across_time_hyper = []
    superior_performance_across_time_hyper = []
    diversity_across_time_hyper = []
    variance_across_time_hyper = []
    for hyper_loop in range(hyper_iteration):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, n, group_size, lr, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        # emerge the hyper_loop
        performance_across_time_hyper += [result[0] for result in results]
        superior_performance_across_time_hyper += [result[1] for result in results]
        diversity_across_time_hyper += [result[2] for result in results]
        variance_across_time_hyper += [result[3] for result in results]

    performance_across_time_final = []
    superior_performance_across_time_final = []
    diversity_across_time_final = []
    variance_across_time_final = []
    for index in range(search_loop):
        temp_performance = sum([result[index] for result in performance_across_time_hyper]) / len(performance_across_time_hyper)
        temp_superior = sum([result[index] for result in superior_performance_across_time_hyper]) / len(superior_performance_across_time_hyper)
        temp_diveristy = sum([result[index] for result in diversity_across_time_hyper]) / len(diversity_across_time_hyper)
        temp_variance = sum([result[index] for result in variance_across_time_hyper]) / len(variance_across_time_hyper)

        performance_across_time_final.append(temp_performance)
        superior_performance_across_time_final.append(temp_superior)
        diversity_across_time_final.append(temp_diveristy)
        variance_across_time_final.append(temp_variance)

    with open("hierarchy_performance", 'wb') as out_file:
        pickle.dump(performance_across_time_final, out_file)
    with open("hierarchy_superior_performance", 'wb') as out_file:
        pickle.dump(superior_performance_across_time_final, out_file)
    with open("hierarchy_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_time_final, out_file)
    with open("hierarchy_variance", 'wb') as out_file:
        pickle.dump(variance_across_time_final, out_file)

    # save the original data to assess the iteration
    with open("hierarchy_original_performance", 'wb') as out_file:
        pickle.dump(performance_across_time_hyper, out_file)
    with open("hierarchy_original_superior_performance", 'wb') as out_file:
        pickle.dump(superior_performance_across_time_hyper, out_file)
    with open("hierarchy_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_time_hyper, out_file)
    with open("hierarchy_original_variance", 'wb') as out_file:
        pickle.dump(variance_across_time_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))





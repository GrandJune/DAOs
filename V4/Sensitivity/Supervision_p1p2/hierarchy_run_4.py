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


def func(m=None, n=None, group_size=None, lr=None, p1=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size, p1=p1, p2=0.9)
    for _ in range(search_loop):
        hierarchy.search()
    performance = hierarchy.performance_across_time[-1]
    superior_performance = hierarchy.superior.performance_average_across_time[-1]
    diversity = hierarchy.diversity_across_time[-1]
    variance = hierarchy.variance_across_time[-1]
    return_dict[loop] = [performance, superior_performance, diversity, variance]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    repetition = 400
    search_loop = 500
    concurrency = 50
    p1_list = [0.65, 0.7, 0.75, 0.8]
    # [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
    p2_list = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
    group_size = 7  # the smallest group size in Fang's model: 7s
    # DVs
    performance_across_p1p2 = []
    superior_performance_across_p1p2 = []
    diversity_across_p1p2 = []
    variance_across_p1p2 = []
    for p1 in p1_list:
        performance_across_p2 = []
        superior_performance_across_p2 = []
        diversity_across_p2 = []
        variance_across_p2 = []
        for p2 in p2_list:
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, p1, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.

            performance_across_repeat = [result[0] for result in results]
            superior_performance_across_repeat = [result[1] for result in results]
            diversity_across_repeat = [result[2] for result in results]
            variance_across_repeat = [result[3] for result in results]


            performance_across_p2.append(sum(performance_across_repeat) / len(performance_across_repeat))
            superior_performance_across_p2.append(
                sum(superior_performance_across_repeat) / len(superior_performance_across_repeat))
            diversity_across_p2.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
            variance_across_p2.append(sum(variance_across_repeat) / len(variance_across_repeat))

        performance_across_p1p2.append(performance_across_p2)
        superior_performance_across_p1p2.append(superior_performance_across_p2)
        diversity_across_p1p2.append(diversity_across_p2)
        variance_across_p1p2.append(variance_across_p2)

    # save the without-time data
    with open("hierarchy_performance_across_p1p2_4", 'wb') as out_file:
        pickle.dump(performance_across_p1p2, out_file)
    with open("superior_performance_across_p1p2_4", 'wb') as out_file:
        pickle.dump(superior_performance_across_p1p2, out_file)
    with open("hierarchy_diversity_across_p1p2_4", 'wb') as out_file:
        pickle.dump(diversity_across_p1p2, out_file)
    with open("hierarchy_variance_across_p1p2_4", 'wb') as out_file:
        pickle.dump(variance_across_p1p2, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))




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
    reality = Reality(m=m, s=s)
    hierarchy = Hierarchy(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size)
    for _ in range(search_loop):
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_across_time, hierarchy.deviation_across_time, hierarchy.diversity_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 1400
    lr = 0.3
    threshold_ratio = 0.1
    repetition = 100
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 30
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        sema.acquire()
        p = mp.Process(target=func, args=(m, s, n, group_size, lr, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.
    performance_across_time = [result[0] for result in results]
    superior_performance_across_time = [result[1] for result in results]
    deviation_across_time = [result[2] for result in results]
    diversity_across_time = [result[3] for result in results]

    performance_across_time_2 = []
    superior_performance_across_time_2 = []
    deviation_across_time_2 = []
    diversity_across_time_2 = []
    for index in range(search_loop):
        temp_1 = sum([result[index] for result in performance_across_time]) / search_loop
        temp_2 = sum([result[index] for result in superior_performance_across_time]) / search_loop
        temp_3 = math.sqrt(sum([result[index] ** 2 for result in deviation_across_time]) / search_loop)  # standard deviation
        temp_4 = sum([result[index] for result in diversity_across_time]) / search_loop
        performance_across_time_2.append(temp_1)
        superior_performance_across_time_2.append(temp_2)
        deviation_across_time_2.append(temp_3)
        diversity_across_time_2.append(temp_4)

    with open("hierarchy_performance_across_time", 'wb') as out_file:
        pickle.dump(performance_across_time_2, out_file)
    with open("hierarchy_superior_performance_across_time", 'wb') as out_file:
        pickle.dump(superior_performance_across_time_2, out_file)
    with open("hierarchy_deviation_across_time", 'wb') as out_file:
        pickle.dump(deviation_across_time_2, out_file)
    with open("hierarchy_diversity_across_time", 'wb') as out_file:
        pickle.dump(diversity_across_time_2, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))



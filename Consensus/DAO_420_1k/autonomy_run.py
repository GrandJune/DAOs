# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: autonomy_run.py
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


def func(m=None, s=None, n=None, group_size=None, lr=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    reality = Reality(m=m, s=s)
    autonomy = Autonomy(m=m, s=s, n=n, reality=reality, subgroup_size=group_size, lr=lr)
    for _ in range(search_loop):
        autonomy.search()
    return_dict[loop] = [autonomy.performance_across_time, autonomy.diversity_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 420
    lr = 0.3
    threshold_ratio = 0.1
    repetition = 1000
    search_loop = 1000
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
    diversity_across_time = [result[1] for result in results]

    performance_across_time_final = []
    diversity_across_time_final = []
    for index in range(search_loop):
        temp_performance = sum([result[index] for result in performance_across_time]) / search_loop
        temp_diversity = sum([result[index] for result in diversity_across_time]) / search_loop
        performance_across_time_final.append(temp_performance)
        diversity_across_time_final.append(temp_diversity)
    with open("autonomy_performance_across_time", 'wb') as out_file:
        pickle.dump(performance_across_time_final, out_file)
    with open("autonomy_diversity_across_time", 'wb') as out_file:
        pickle.dump(diversity_across_time_final, out_file)

    # save the original data to assess the iteration
    with open("autonomy_original_performance", 'wb') as out_file:
        pickle.dump(performance_across_time, out_file)
    with open("autonomy_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_time, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

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


def func(m=None, n=None, group_size=None, lr=None, search_loop=None,
         loop=None, return_dict=None, sema=None):
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
    # 50 groups
    group_size_list = []
    for _ in range(50):
        group_size_list.append(np.random.randint(5, 21))
    n = 420
    lr = 0.3
    repetition = 400
    concurrency = 100
    search_loop = 300

    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        sema.acquire()
        p = mp.Process(target=func,
                       args=(m, n, group_size_list, lr, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.

    # remove the time dimension, only keep the last value
    performance_across_repeat = [result[0] for result in results]
    superior_performance_across_repeat = [result[1] for result in results]
    diversity_across_repeat = [result[2] for result in results]
    variance_across_repeat = [result[3] for result in results]

    performance_list = np.mean(performance_across_repeat, axis=0)
    superior_performance_list = np.mean(superior_performance_across_repeat, axis=0)
    diversity_list = np.mean(diversity_across_repeat, axis=0)
    variance_list = np.mean(variance_across_repeat, axis=0)

    with open("hierarchy_performance_across_time", 'wb') as out_file:
        pickle.dump(performance_list, out_file)
    with open("superior_performance_across_time", 'wb') as out_file:
        pickle.dump(superior_performance_list, out_file)
    with open("hierarchy_diversity_across_time", 'wb') as out_file:
        pickle.dump(diversity_list, out_file)
    with open("hierarchy_variance_across_time", 'wb') as out_file:
        pickle.dump(variance_list, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))





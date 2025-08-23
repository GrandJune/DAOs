# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO_inequal_size import DAO
from Hierarchy import Hierarchy
from Autonomy import Autonomy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Pool
from multiprocessing import Semaphore
import pickle
import math


def func(m=None, n=None, group_size_list=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size_list=group_size_list)
    for _ in range(search_loop):
        dao.search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    # 50 groups
    group_size_list = []
    for _ in range(50):
        group_size_list.append(np.random.randint(5, 21))
    # group_size_list = [7, 14, 21, 28]
    n = 420
    lr = 0.3
    repetition = 400
    concurrency = 100
    search_loop = 300
    threshold_ratio = 0.5

    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        sema.acquire()
        p = mp.Process(target=func, args=(m, n, group_size_list, lr, threshold_ratio, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.

    # remove the time dimension, only keep the last value
    performance_across_repeat = [result[0] for result in results]
    consensus_performance_across_repeat = [result[1] for result in results]
    diversity_across_repeat = [result[2] for result in results]
    variance_across_repeat = [result[3] for result in results]

    performance_list = np.mean(performance_across_repeat, axis=0)
    cosensus_list = np.mean(consensus_performance_across_repeat, axis=0)
    diversity_list = np.mean(diversity_across_repeat, axis=0)
    variance_list = np.mean(variance_across_repeat, axis=0)

    # save the with-time data
    with open("dao_performance_across_time", 'wb') as out_file:
        pickle.dump(performance_list, out_file)
    with open("consensus_performance_across_time", 'wb') as out_file:
        pickle.dump(cosensus_list, out_file)
    with open("dao_diversity_across_time", 'wb') as out_file:
        pickle.dump(diversity_list, out_file)
    with open("dao_variance_across_time", 'wb') as out_file:
        pickle.dump(variance_list, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


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


def func(m=None, n=None, group_size=None, lr=None, p1=None, p2=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size, p1=p1, p2=p2)
    for _ in range(search_loop):
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    repetition = 320
    search_loop = 500
    concurrency = 80
    p1_list = np.arange(0.05, 1.0, 0.05)
    p2_list = np.arange(0.25, 0.50, 0.05)
    group_size = 7  # the smallest group size in Fang's model: 7
    # DVs
    performance_across_p1p2 = []
    for p1 in p1_list: # learning from code
        performance_across_p2 = []
        for p2 in p2_list:  # learning from individuals
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, p1, p2, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.
            # remove the time dimension, only keep the last value
            performance_across_repeat = [result[0][-1] for result in results]
            performance_across_p2.append(sum(performance_across_repeat) / len(performance_across_repeat))
        performance_across_p1p2.append(performance_across_p2)
    # save the without-time data
    with open("hierarchy_performance_2", 'wb') as out_file:
        pickle.dump(performance_across_p1p2, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))




# -*- coding: utf-8 -*-
# @Time     : 6/8/2023 15:05
# @Author   : Junyi
# @FileName: run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
# Heterogeneous vs. Homogeneous Learners
# Figure 1: varying p1 and p2
from Organization import Organization
from Individual import Individual
from Reality import Reality
import numpy as np
import pickle
import multiprocessing as mp
import time
from multiprocessing import Pool
from multiprocessing import Semaphore


def func(p1=None, p2=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    organization = Organization(m=m, n=n, p1=p1, p2=p2, reality=reality)
    organization.process(search_round=200)
    return_dict[loop] = [organization.performance_curve]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    repetition = 100
    search_loop = 200
    concurrency = 50
    p1_list = np.arange(0.1, 1.0, 0.1)
    p2_list = np.arange(0.1, 0.50, 0.1)
    group_size = 7  # the smallest group size in Fang's model: 7
    # DVs
    performance_across_p1p2 = []
    for p1 in p1_list:
        performance_across_p2 = []
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
            # remove the time dimension, only keep the last value
            performance_across_repeat = [result[0][-1] for result in results]
            performance_across_p2.append(sum(performance_across_repeat) / len(performance_across_repeat))
        performance_across_p1p2.append(performance_across_p2)
        # save the without-time data
        with open("hierarchy_performance", 'wb') as out_file:
            pickle.dump(performance_across_p1p2, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
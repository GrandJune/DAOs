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


def func(m=None, s=None, n=None, group_size=None, auto_lr=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size)
    for _ in range(search_loop):
        dao.search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time]
    sema.release()



if __name__ == '__main__':
    t0 = time.time()
    m = 30
    s = 1
    n = 7000
    auto_lr = 0.3
    lr = 0.3
    repetition = 100
    search_loop = 100
    threshold_ratio_list = np.arange(0, 0.30, 0.05)
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_across_para = []
    consensus_performance_across_para = []
    concurrency = 30
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for threshold_ratio in threshold_ratio_list:
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, s, n, group_size, auto_lr, lr, threshold_ratio,
         search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_across_time = [result[0][-1] for result in results]
        consensus_performance_across_time = [result[1][-1] for result in results]
        performance_across_para.append(sum(performance_across_time) / len(performance_across_time))
        consensus_performance_across_para.append(sum(consensus_performance_across_time) / len(consensus_performance_across_time))

    with open("dao_performance_across_threshold", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("dao_consensus_performance_across_threshold", 'wb') as out_file:
        pickle.dump(consensus_performance_across_para, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

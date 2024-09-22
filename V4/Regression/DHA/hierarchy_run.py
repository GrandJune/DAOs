# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
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
import os


def func(m=None, n=None, group_size=None, lr=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time[-1], hierarchy.diversity_across_time[-1], m, n, group_size, lr]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    np.random.seed(None)
    group_num_list = [100, 75, 50, 25]
    group_size_list = [7, 14, 21, 28]
    m_list = [60, 90, 120, 150]
    lr_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    repetition = 100
    search_loop = 300

    concurrency = 50
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    jobs = []
    return_dict = manager.dict()
    for loop in range(repetition):
        # Randomization
        m = np.random.choice(m_list)
        group_num = np.random.choice(group_num_list)
        group_size = np.random.choice(group_size_list)  # 28*40=1120; 10*7=70
        n = group_size * group_num
        lr = np.random.choice(lr_list)

        sema.acquire()
        p = mp.Process(target=func, args=(m, n, group_size, lr, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.
    # Automatic integration of results
    time.sleep(np.random.uniform(low=2, high=60))
    if os.path.exists("hierarchy_data"):
        with open("hierarchy_data", 'rb') as infile:
            prior_results = pickle.load(infile)
            results += prior_results
    with open("hierarchy_data", 'wb') as out_file:
        pickle.dump(results, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

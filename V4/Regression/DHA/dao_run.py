# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO import DAO
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle
import os


def func(m=None, n=None, group_size=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        dao.search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time[-1], dao.diversity_across_time[-1], m, n, group_size, lr]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    np.random.seed(None)
    threshold_ratio = 0.5  # Fix parameters of interest
    lr_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    repetition = 100
    search_loop = 300
    concurrency = 100
    data = []
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        # Randomization
        m = 90
        group_num = 50
        group_size = 7
        n = group_size * group_num
        lr = np.random.choice(lr_list)
        sema.acquire()
        p = mp.Process(target=func,
                       args=(m, n, group_size, lr, threshold_ratio, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.

    # Automatic integration of results
    time.sleep(np.random.uniform(low=2, high=60))
    if os.path.exists("dao_data"):
        with open("dao_data", 'rb') as infile:
            prior_results = pickle.load(infile)
            results += prior_results
    with open("dao_data", 'wb') as out_file:
        pickle.dump(results, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


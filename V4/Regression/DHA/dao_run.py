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
    repetition = 200
    search_loop = 300

    # Randomization
    m0 = np.random.randint(30, 50)
    m = m0 * 3
    group_num = np.random.randint(10, 40)
    group_size = np.random.randint(7, 28)  # 28*40=1120; 10*7=70
    n = group_size * group_num
    lr = np.random.uniform(0, 1)

    concurrency = 50
    data = []
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        sema.acquire()
        p = mp.Process(target=func,
                       args=(m, n, group_size, lr, threshold_ratio, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.

    index = 1
    while os.path.exists(r"dao_data_{0}".format(index)):
        index += 1

    with open(r"dao_data_{0}".format(index), 'wb') as out_file:
        pickle.dump(results, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


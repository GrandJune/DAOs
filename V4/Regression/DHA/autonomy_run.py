# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: autonomy_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Autonomy import Autonomy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle


def func(m=None, n=None, group_size=None, lr=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    autonomy = Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr)
    for _ in range(search_loop):
        autonomy.search()
    return_dict[loop] = [autonomy.performance_across_time[-1], autonomy.diversity_across_time[-1], m, n, group_size, lr]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    print("Tess")
    np.random.seed(None)
    hyper_iteration = 40
    repetition = 50
    concurrency = 50
    search_loop = 300

    data = []
    for hyper_loop in range(hyper_iteration):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            # Randomization
            m0 = np.random.randint(30, 50)
            m = m0 * 3
            group_num = np.random.randint(10, 40)
            group_size = np.random.randint(7, 28)  # 28*40=1120; 10*7=70
            n = group_size * group_num
            lr = np.random.uniform(0, 1)

            sema.acquire()
            p = mp.Process(target=func, args=(m, n, group_size, lr, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        data += results

    with open("autonomy_data", 'wb') as out_file:
        pickle.dump(data, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

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


def func(m=None, s=None, n=None, group_size=None, lr=None, search_loop=None, loop=None, return_dict=None, sema=None):
    reality = Reality(m=m, s=s)
    hierarchy = Hierarchy(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size, p1=0.1, p2=0.9)
    for period in range(search_loop):
        if (period + 1) % 200 == 0:
            reality.change(reality_change_rate=0.1)
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_average_across_time, hierarchy.diversity_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 420
    lr = 0.3
    repetition = 400
    search_loop = 1000
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 100
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []

    performance_final = []
    superior_final = []
    diversity_final = []
    for loop in range(repetition):
        sema.acquire()
        p = mp.Process(target=func,
                       args=(m, s, n, group_size, lr, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.
    performance_across_repeat = [result[0] for result in results]
    superior_performance_across_repeat = [result[1] for result in results]
    diversity_across_repeat = [result[2] for result in results]
    for period in range(search_loop):
        performance_temp = [performance_list[period] for performance_list in performance_across_repeat]
        superior_temp = [superior_list[period] for superior_list in superior_performance_across_repeat]
        diversity_temp = [diversity_list[period] for diversity_list in diversity_across_repeat]
        performance_final.append(sum(performance_temp) / len(performance_temp))
        superior_final.append(sum(superior_temp) / len(superior_temp))
        diversity_final.append(sum(diversity_temp) / len(diversity_temp))

    with open("hierarchy_performance", 'wb') as out_file:
        pickle.dump(performance_final, out_file)
    with open("hierarchy_superior_performance", 'wb') as out_file:
        pickle.dump(superior_final, out_file)
    with open("hierarchy_diversity", 'wb') as out_file:
        pickle.dump(diversity_final, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

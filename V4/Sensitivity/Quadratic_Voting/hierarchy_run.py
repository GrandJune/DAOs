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


def func(m=None, n=None, group_size=None, lr=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_average_across_time,
                         hierarchy.diversity_across_time, hierarchy.variance_across_time, hierarchy.cv_across_time, hierarchy.entropy_across_time, hierarchy.antagonism_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    hyper_iteration = 10
    repetition = 50
    concurrency = 50
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_across_time_hyper = []
    superior_performance_across_time_hyper = []
    diversity_across_time_hyper = []
    variance_across_time_hyper = []
    cv_across_time_hyper = []
    entropy_across_time_hyper = []
    antagonism_across_time_hyper = []
    for hyper_loop in range(hyper_iteration):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, n, group_size, lr, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        # emerge the hyper_loop
        performance_across_time_hyper += [result[0] for result in results]
        superior_performance_across_time_hyper += [result[1] for result in results]
        diversity_across_time_hyper += [result[2] for result in results]
        variance_across_time_hyper += [result[3] for result in results]
        cv_across_time_hyper += [result[4] for result in results]
        entropy_across_time_hyper += [result[5] for result in results]
        antagonism_across_time_hyper += [result[6] for result in results]

    performance_across_time_final = np.mean(performance_across_time_hyper, axis=0).tolist()
    superior_performance_across_time_final = np.mean(superior_performance_across_time_hyper, axis=0).tolist()
    diversity_across_time_final = np.mean(diversity_across_time_hyper, axis=0).tolist()
    variance_across_time_final = np.mean(variance_across_time_hyper, axis=0).tolist()
    cv_across_time_final = np.mean(cv_across_time_hyper, axis=0).tolist()
    entropy_across_time_final = np.mean(entropy_across_time_hyper, axis=0).tolist()
    antagonism_across_time_final = np.mean(antagonism_across_time_hyper, axis=0).tolist()

    with open("hierarchy_performance", 'wb') as out_file:
        pickle.dump(performance_across_time_final, out_file)
    with open("hierarchy_superior_performance", 'wb') as out_file:
        pickle.dump(superior_performance_across_time_final, out_file)
    with open("hierarchy_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_time_final, out_file)
    with open("hierarchy_variance", 'wb') as out_file:
        pickle.dump(variance_across_time_final, out_file)
    with open("hierarchy_cv", 'wb') as out_file:
        pickle.dump(cv_across_time_final, out_file)
    with open("hierarchy_entropy", 'wb') as out_file:
        pickle.dump(entropy_across_time_final, out_file)
    with open("hierarchy_antagonism", 'wb') as out_file:
        pickle.dump(antagonism_across_time_final, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Hierarchy", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))  # Complete time


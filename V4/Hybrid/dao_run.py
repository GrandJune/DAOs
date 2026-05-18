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


def func(m=None, n=None, group_size=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        dao.search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time, dao.cv_across_time, dao.entropy_across_time, dao.antagonism_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    threshold_ratio = 0.5
    hyper_iteration = 10
    repetition = 50
    concurrency = 50
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_hyper = []
    consensus_hyper = []
    diversity_hyper = []
    variance_hyper = []
    cv_hyper = []
    entropy_hyper = []
    antagonism_hyper = []
    for hyper_loop in range(hyper_iteration):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, n, group_size, lr, threshold_ratio, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_hyper += [result[0] for result in results]
        consensus_hyper += [result[1] for result in results]
        diversity_hyper += [result[2] for result in results]
        variance_hyper += [result[3] for result in results]
        cv_hyper += [result[4] for result in results]
        entropy_hyper += [result[5] for result in results]
        antagonism_hyper += [result[6] for result in results]

    # Convert lists of lists to NumPy arrays
    performance_final = np.mean(performance_hyper, axis=0).tolist()
    consensus_final = np.mean(consensus_hyper, axis=0).tolist()
    diversity_final = np.mean(diversity_hyper, axis=0).tolist()
    variance_final = np.mean(variance_hyper, axis=0).tolist()
    cv_final = np.mean(cv_hyper, axis=0).tolist()
    entropy_final = np.mean(entropy_hyper, axis=0).tolist()
    antagonism_final = np.mean(antagonism_hyper, axis=0).tolist()

    with open("dao_performance", 'wb') as out_file:
        pickle.dump(performance_final, out_file)
    with open("dao_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_final, out_file)
    with open("dao_diversity", 'wb') as out_file:
        pickle.dump(diversity_final, out_file)
    with open("dao_variance", 'wb') as out_file:
        pickle.dump(variance_final, out_file)
    with open("dao_cv", 'wb') as out_file:
        pickle.dump(cv_final, out_file)
    with open("dao_entropy", 'wb') as out_file:
        pickle.dump(entropy_final, out_file)
    with open("dao_antagonism", 'wb') as out_file:
        pickle.dump(antagonism_final, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("DAO", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))  # Complete time


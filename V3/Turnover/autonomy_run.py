# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: autonomy_run.py
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


def func(m=None, s=None, n=None, group_size=None, lr=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    autonomy = Autonomy(m=m, s=s, n=n, reality=reality, group_size=group_size, lr=lr)
    for period in range(search_loop):
        autonomy.turnover(turnover_rate=0.01)
        autonomy.search()
    return_dict[loop] = [autonomy.performance_across_time, autonomy.diversity_across_time, autonomy.variance_across_time,
                         autonomy.variance_across_time, autonomy.percentile_10_across_time, autonomy.percentile_90_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 350
    lr = 0.3
    hyper_iteration = 4
    repetition = 50
    search_loop = 1000
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 50
    # after taking an average across repetitions
    performance_final = []
    consensus_final = []
    diversity_final = []
    variance_final = []
    percentile_10_final = []
    percentile_90_final = []
    # before taking an average across repetitions
    performance_hyper = []
    consensus_hyper = []
    diversity_hyper = []
    variance_hyper = []
    percentile_10_hyper = []
    percentile_90_hyper = []
    for hyper_loop in range(hyper_iteration):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, s, n, group_size, lr, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_hyper += [result[0] for result in results]
        diversity_hyper += [result[1] for result in results]
        variance_hyper += [result[2] for result in results]
        percentile_10_hyper += [result[3] for result in results]
        percentile_90_hyper += [result[4] for result in results]
    for period in range(search_loop):
        performance_temp = [performance_list[period] for performance_list in performance_hyper]
        diversity_temp = [diversity_list[period] for diversity_list in diversity_hyper]
        variance_temp = [variance_list[period] for variance_list in variance_hyper]
        percentile_10_temp = [percentile_10_list[period] for percentile_10_list in percentile_10_hyper]
        percentile_90_temp = [percentile_90_list[period] for percentile_90_list in percentile_90_hyper]

        performance_final.append(sum(performance_temp) / len(performance_temp))
        diversity_final.append(sum(diversity_temp) / len(diversity_temp))
        variance_final.append(sum(variance_temp) / len(variance_temp))
        percentile_10_final.append(sum(percentile_10_temp) / len(percentile_10_temp))
        percentile_90_final.append(sum(percentile_90_temp) / len(percentile_90_temp))

    # after taking an average across repetitions
    with open("autonomy_performance", 'wb') as out_file:
        pickle.dump(performance_final, out_file)
    with open("autonomy_diversity", 'wb') as out_file:
        pickle.dump(diversity_final, out_file)
    with open("autonomy_variance", 'wb') as out_file:
        pickle.dump(variance_final, out_file)
    with open("autonomy_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_final, out_file)
    with open("autonomy_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_final, out_file)

    # before taking an average across repetitions
    with open("autonomy_original_performance", 'wb') as out_file:
        pickle.dump(performance_hyper, out_file)
    with open("autonomy_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_hyper, out_file)
    with open("autonomy_original_variance", 'wb') as out_file:
        pickle.dump(variance_hyper, out_file)
    with open("autonomy_original_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_hyper, out_file)
    with open("autonomy_original_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

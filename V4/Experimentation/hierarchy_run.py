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


def func(m=None, n=None, group_size=None, lr=None, experimentation_rate=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size, p1=0.1, p2=0.9)
    for period in range(search_loop):
        hierarchy.experimentation(experimentation_rate=experimentation_rate)
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_average_across_time,
                         hierarchy.diversity_across_time, hierarchy.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    experimentation_rate_list = [0.02, 0.04, 0.06, 0.08, 0.10]
    group_size = 7
    n = 350
    lr = 0.3
    repetition = 300
    concurrency = 100
    search_loop = 1000
    # DVs
    performance_across_para = []
    superior_performance_across_para = []
    diversity_across_para = []
    variance_across_para = []

    performance_across_para_time = []
    superior_performance_across_para_time = []
    diversity_across_para_time = []
    variance_across_para_time = []
    for experimentation_rate in experimentation_rate_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, n, group_size, lr, experimentation_rate, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.

        # remove the time dimension, only keep the last value
        performance_across_repeat = [result[0][-1] for result in results]
        superior_performance_across_repeat = [result[1][-1] for result in results]
        diversity_across_repeat = [result[2][-1] for result in results]
        variance_across_repeat = [result[3][-1] for result in results]

        # take an average across repetition, only one value for one parameter
        performance_across_para.append(sum(performance_across_repeat) / len(performance_across_repeat))
        superior_performance_across_para.append(
            sum(superior_performance_across_repeat) / len(superior_performance_across_repeat))
        diversity_across_para.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
        variance_across_para.append(sum(variance_across_repeat) / len(variance_across_repeat))

        # keep the time dimension
        performance_across_repeat_time = [result[0] for result in results]
        superior_performance_across_repeat_time = [result[1] for result in results]
        diversity_across_repeat_time = [result[2] for result in results]
        variance_across_repeat_time = [result[3] for result in results]

        # take an average across repetition, for each time iteration, integrate into 600 values for one parameter
        performance_across_time = []  # under the same parameter
        superior_performance_across_time = []
        diversity_across_time = []
        variance_across_time = []
        for period in range(search_loop):
            temp_performance = [performance_list[period] for performance_list in performance_across_repeat_time]
            performance_across_time.append(sum(temp_performance) / len(temp_performance))
            temp_superior_performance = [performance_list[period] for performance_list in
                                         superior_performance_across_repeat_time]
            superior_performance_across_time.append(sum(temp_superior_performance) / len(temp_superior_performance))

            temp_diversity = [diversity_list[period] for diversity_list in diversity_across_repeat_time]
            diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))

            temp_variance = [variance_list[period] for variance_list in variance_across_repeat_time]
            variance_across_time.append(sum(temp_variance) / len(temp_variance))
        # retain the time dimension
        performance_across_para_time.append(performance_across_time)
        superior_performance_across_para_time.append(superior_performance_across_time)
        diversity_across_para_time.append(diversity_across_time)
        variance_across_para_time.append(variance_across_time)

    # save the without-time data
    with open("hierarchy_performance_across_experimentation", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("superior_performance_across_experimentation", 'wb') as out_file:
        pickle.dump(superior_performance_across_para, out_file)
    with open("hierarchy_diversity_across_experimentation", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("hierarchy_variance_across_experimentation", 'wb') as out_file:
        pickle.dump(variance_across_para, out_file)

    # save the with-time data
    with open("hierarchy_performance_across_experimentation_time", 'wb') as out_file:
        pickle.dump(performance_across_para_time, out_file)
    with open("superior_performance_across_experimentation_time", 'wb') as out_file:
        pickle.dump(superior_performance_across_para_time, out_file)
    with open("hierarchy_diversity_across_experimentation_time", 'wb') as out_file:
        pickle.dump(diversity_across_para_time, out_file)
    with open("hierarchy_variance_across_experimentation_time", 'wb') as out_file:
        pickle.dump(variance_across_para_time, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
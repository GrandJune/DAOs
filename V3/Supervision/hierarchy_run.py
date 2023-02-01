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


def func(m=None, s=None, n=None, group_size=None, lr=None, p1=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    hierarchy = Hierarchy(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size, p1=p1, p2=0.9)
    for _ in range(search_loop):
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_average_across_time, hierarchy.diversity_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 60
    s = 1
    n = 350
    lr = 0.3
    repetition = 50
    search_loop = 200
    p1_list = np.arange(0.1, 1.0, 0.1)
    group_size = 7  # the smallest group size in Fang's model: 7
    # DVs
    performance_across_para = []
    superior_performance_across_para = []
    deviation_across_para = []
    diversity_across_para = []

    performance_across_para_time = []
    diversity_across_para_time = []
    superior_performance_across_para_time = []
    concurrency = 50
    for p1 in p1_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, s, n, group_size, lr, p1, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.

        # remove the time dimension, only keep the last value
        performance_across_repeat = [result[0][-1] for result in results]
        superior_performance_across_repeat = [result[1][-1] for result in results]
        diversity_across_repeat = [result[2][-1] for result in results]
        deviation_across_repeat = np.std(performance_across_repeat)

        # take an average across repetition, only one value for one parameter
        performance_across_para.append(sum(performance_across_repeat) / len(performance_across_repeat))
        superior_performance_across_para.append(sum(superior_performance_across_repeat) / len(superior_performance_across_repeat))
        diversity_across_para.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
        deviation_across_para.append(deviation_across_repeat)

        # keep the time dimension
        performance_across_repeat_time = [result[0] for result in results]
        superior_performance_across_repeat_time = [result[1] for result in results]
        diversity_across_repeat_time = [result[2] for result in results]

        # take an average across repetition, for each time iteration, integrate into 600 values for one parameter
        performance_across_time = []  # under the same parameter
        superior_performance_across_time = []
        diversity_across_time = []
        for time in range(search_loop):
            temp_performance = [performance_list[time] for performance_list in performance_across_repeat_time]
            performance_across_time.append(sum(temp_performance) / len(temp_performance))

            temp_superior_performance = [performance_list[time] for performance_list in superior_performance_across_repeat_time]
            superior_performance_across_time.append(sum(temp_superior_performance) / len(temp_superior_performance))

            temp_diversity = [diversity_list[time] for diversity_list in diversity_across_repeat_time]
            diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))
        # retain the time dimension
        performance_across_para_time.append(performance_across_time)
        superior_performance_across_para_time.append(superior_performance_across_time)
        diversity_across_para_time.append(diversity_across_time)

    # save the without-time data
    with open("hierarchy_performance_across_threshold", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("superior_performance_across_threshold", 'wb') as out_file:
        pickle.dump(superior_performance_across_para, out_file)
    with open("hierarchy_diversity_across_threshold", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("hierarchy_deviation_across_threshold", 'wb') as out_file:
        pickle.dump(deviation_across_para, out_file)

    # save the with-time data
    with open("hierarchy_performance_across_threshold_time", 'wb') as out_file:
        pickle.dump(performance_across_para_time, out_file)
    with open("superior_performance_across_threshold_time", 'wb') as out_file:
        pickle.dump(superior_performance_across_para_time, out_file)
    with open("hierarchy_diversity_across_threshold_time", 'wb') as out_file:
        pickle.dump(diversity_across_para_time, out_file)

    import matplotlib.pyplot as plt
    from matplotlib import container

    x = p1_list
    fig, (ax1) = plt.subplots(1, 1)
    ax1.errorbar(x, performance_across_para, yerr=deviation_across_para, color="k", fmt="--", capsize=5, capthick=0.8,
                 ecolor="k", label="Hierarchy")
    plt.xlabel('P1', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.xticks(x)
    handles, labels = ax1.get_legend_handles_labels()
    handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
    plt.legend(handles, labels, numpoints=1)
    plt.savefig("Performance_across_P1.png", transparent=True, dpi=500)
    plt.clf()
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))




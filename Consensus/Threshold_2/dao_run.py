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
from matplotlib import container
import pickle
import math


def func(m=None, s=None, n=None, group_size=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size)
    for _ in range(search_loop):
        dao.search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time, dao.diversity_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 1400
    lr = 0.3
    repetition = 100
    search_loop = 1000
    threshold_ratio_list = np.arange(0, 0.21, 0.01)
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_across_para = []
    consensus_performance_across_para = []
    deviation_across_para = []
    diversity_across_para = []
    concurrency = 30
    for threshold_ratio in threshold_ratio_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, s, n, group_size, lr, threshold_ratio, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_across_repeat = [result[0][-1] for result in results]
        consensus_performance_across_repeat = [result[1][-1] for result in results]
        diversity_across_repeat = [result[2][-1] for result in results]
        deviation_across_repeat = np.std(performance_across_repeat)

        performance_across_para.append(sum(performance_across_repeat) / len(performance_across_repeat))
        consensus_performance_across_para.append(sum(consensus_performance_across_repeat) / len(consensus_performance_across_repeat))
        diversity_across_para.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
        deviation_across_para.append(deviation_across_repeat)

    with open("dao_performance_across_threshold", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("dao_consensus_performance_across_threshold", 'wb') as out_file:
        pickle.dump(consensus_performance_across_para, out_file)
    with open("dao_diversity_across_threshold", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("dao_deviation_across_threshold", 'wb') as out_file:
        pickle.dump(deviation_across_para, out_file)


    import matplotlib.pyplot as plt
    from matplotlib import container
    x = threshold_ratio_list
    fig, (ax1) = plt.subplots(1, 1)
    ax1.errorbar(x, performance_across_para, yerr=deviation_across_para, color="k", fmt="--", capsize=5, capthick=0.8, ecolor="k", label="DAO")
    plt.xlabel('Threshold', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.xticks(x)
    handles, labels = ax1.get_legend_handles_labels()
    handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
    plt.legend(handles, labels, numpoints=1)
    plt.savefig("Performance_across_threshold.png", transparent=True, dpi=500)
    plt.clf()
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

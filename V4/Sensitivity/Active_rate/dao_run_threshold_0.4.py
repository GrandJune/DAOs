# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO_active import DAO
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle



def func(m=None, n=None, group_size=None, lr=None, active_rate=None, threshold_ratio=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for _ in range(search_loop):
        # randomly select active voters
        for team in dao.teams:
            for individual in team.individuals:
                if np.random.uniform(0, 1) < active_rate:
                    individual.active = 1
                else:
                    individual.active = 0
        dao.active_search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()



if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    active_rate_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    repetition = 500
    concurrency = 100
    search_loop = 500
    group_size = 7  # the smallest group size in Fang's model: 7
    lr = 0.3
    threshold_ratio = 0.4
    # DVs
    performance_across_para = []
    consensus_performance_across_para = []
    diversity_across_para = []
    variance_across_para = []

    performance_across_para_time = []
    consensus_performance_across_para_time = []
    diversity_across_para_time = []
    variance_across_para_time = []
    for active_rate in active_rate_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, n, group_size, lr, active_rate, threshold_ratio, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.

        # remove the time dimension, only keep the last value
        performance_across_repeat = [result[0][-1] for result in results]
        consensus_performance_across_repeat = [result[1][-1] for result in results]
        diversity_across_repeat = [result[2][-1] for result in results]
        variance_across_repeat = [result[3][-1] for result in results]

        # take an average across repetition, only one value for one parameter
        performance_across_para.append(sum(performance_across_repeat) / len(performance_across_repeat))
        consensus_performance_across_para.append(
            sum(consensus_performance_across_repeat) / len(consensus_performance_across_repeat))
        diversity_across_para.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
        variance_across_para.append(sum(variance_across_repeat) / len(variance_across_repeat))

        # keep the time dimension
        performance_across_repeat_time = [result[0] for result in results]
        consensus_performance_across_repeat_time = [result[1] for result in results]
        diversity_across_repeat_time = [result[2] for result in results]
        variance_across_repeat_time = [result[3] for result in results]

        # take an average across repetition, for each time iteration, integrate into 600 values for one parameter
        performance_across_time = []  # under the same parameter
        consensus_performance_across_time = []
        diversity_across_time = []
        variance_across_time = []
        for period in range(search_loop):
            temp_performance = [performance_list[period] for performance_list in performance_across_repeat_time]
            performance_across_time.append(sum(temp_performance) / len(temp_performance))
            temp_consensus_performance = [performance_list[period] for performance_list in
                                         consensus_performance_across_repeat_time]
            consensus_performance_across_time.append(sum(temp_consensus_performance) / len(temp_consensus_performance))

            temp_diversity = [diversity_list[period] for diversity_list in diversity_across_repeat_time]
            diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))

            temp_variance = [variance_list[period] for variance_list in variance_across_repeat_time]
            variance_across_time.append(sum(temp_variance) / len(temp_variance))
        # retain the time dimension
        performance_across_para_time.append(performance_across_time)
        consensus_performance_across_para_time.append(consensus_performance_across_time)
        diversity_across_para_time.append(diversity_across_time)
        variance_across_para_time.append(variance_across_time)

    # save the without-time data (ready for figure)
    with open("dao_performance_across_active_rate_{0}".format(threshold_ratio), 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("consensus_performance_across_active_rate_{0}".format(threshold_ratio), 'wb') as out_file:
        pickle.dump(consensus_performance_across_para, out_file)
    with open("dao_diversity_across_active_rate_{0}".format(threshold_ratio), 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("dao_variance_across_active_rate_{0}".format(threshold_ratio), 'wb') as out_file:
        pickle.dump(variance_across_para, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


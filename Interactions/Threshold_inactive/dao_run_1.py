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


def func(m=None, n=None, group_size=None, lr=None, threshold_ratio=None, inactive=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for team in dao.teams:
        for individual in team.individuals:
            individual.token = 1
    for _ in range(search_loop):
        dao.incentive_search(threshold_ratio=threshold_ratio, incentive=0, inactive_rate=inactive)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    repetition = 200
    search_loop = 2000
    threshold_ratio_list = np.arange(0.40, 0.71, 0.01)
    inactive_list = [0.1]
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 100
    for inactive in inactive_list:
        performance_across_para = []  # remove the time dimension
        consensus_performance_across_para = []
        diversity_across_para = []
        variance_across_para = []

        performance_across_para_time = []  # retain the across_time dimension
        consensus_performance_across_para_time = []
        diversity_across_para_time = []
        variance_across_para_time = []
        for threshold_ratio in threshold_ratio_list:
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, threshold_ratio, inactive, search_loop, loop, return_dict, sema))
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

            # take an average across repetition, integrate into one value for one parameter
            performance_across_para.append(sum(performance_across_repeat) / len(performance_across_repeat))
            consensus_performance_across_para.append(
                sum(consensus_performance_across_repeat) / len(consensus_performance_across_repeat))
            diversity_across_para.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
            variance_across_para.append(sum(variance_across_repeat) / len(variance_across_repeat))

            # retain the time dimension
            performance_across_repeat_time = [result[0] for result in results]
            consensus_performance_across_repeat_time = [result[1] for result in results]
            diversity_across_repeat_time = [result[2] for result in results]
            variance_across_repeat_time = [result[3] for result in results]

            # take an average across repetition, for each time iteration, integrate into 600 values for one parameter
            performance_across_time = []  # under the same parameter
            consensus_performance_across_time = []
            diversity_across_time = []
            variance_across_time = []
            for iteration in range(search_loop):
                temp_performance = [performance_list[iteration] for performance_list in performance_across_repeat_time]
                performance_across_time.append(sum(temp_performance) / len(temp_performance))

                temp_consensus = [consensus_list[iteration] for consensus_list in consensus_performance_across_repeat_time]
                consensus_performance_across_time.append(sum(temp_consensus) / len(temp_consensus))

                temp_diversity = [diversity_list[iteration] for diversity_list in diversity_across_repeat_time]
                diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))

                temp_variance = [variance_list[iteration] for variance_list in variance_across_repeat_time]
                variance_across_time.append(sum(temp_variance) / len(temp_variance))
            # retain the time dimension
            performance_across_para_time.append(performance_across_time)
            consensus_performance_across_para_time.append(consensus_performance_across_time)
            diversity_across_para_time.append(diversity_across_time)
            variance_across_para_time.append(variance_across_time)

        # save the without-time data (ready for figure)
        with open("dao_performance_across_threshold_{0}".format(inactive), 'wb') as out_file:
            pickle.dump(performance_across_para, out_file)
        with open("dao_consensus_performance_across_threshold_{0}".format(inactive), 'wb') as out_file:
            pickle.dump(consensus_performance_across_para, out_file)
        with open("dao_diversity_across_threshold_{0}".format(inactive), 'wb') as out_file:
            pickle.dump(diversity_across_para, out_file)
        with open("dao_variance_across_threshold_{0}".format(inactive), 'wb') as out_file:
            pickle.dump(variance_across_para, out_file)

        # save the with-time data
        with open("dao_performance_across_threshold_time_{0}".format(inactive), 'wb') as out_file:
            pickle.dump(performance_across_para_time, out_file)
        with open("dao_consensus_performance_across_threshold_time_{0}".format(inactive), 'wb') as out_file:
            pickle.dump(consensus_performance_across_para_time, out_file)
        with open("dao_diversity_across_threshold_time_{0}".format(inactive), 'wb') as out_file:
            pickle.dump(diversity_across_para_time, out_file)
        with open("dao_variance_across_threshold_time_{0}".format(inactive), 'wb') as out_file:
            pickle.dump(variance_across_para_time, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

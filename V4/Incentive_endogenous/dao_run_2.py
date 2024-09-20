# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO_incentive import DAO
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle
import os


def func(m=None, n=None, group_size=None, lr=None, incentive=None, sensitivity=None,
         active_rate=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, sensitivity=sensitivity)
    # Initialized with equal token
    for team in dao.teams:
        for individual in team.individuals:
            individual.token = 1
    for period in range(search_loop):
        dao.incentive_search(threshold_ratio=0.5, incentive=incentive, basic_active_rate=active_rate)

    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    np.random.seed(None)
    m = 90
    n = 350
    lr = 0.3
    repetition = 50
    search_loop = 300
    incentive_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # * 9
    # active_rate_list = [0.9, 0.8, 0.7, 0.6, 0.5]  # * 5
    # sensitivity_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # * 9
    sensitivity_list = [4, 5, 6]
    group_size = 7  # the smallest group size in Fang's model: 7

    concurrency = 50
    active_rate = 0.8
    performance_final_across_sensitivity_incentive = []
    consensus_final_across_sensitivity_incentive = []
    diversity_final_across_sensitivity_incentive = []
    variance_final_across_sensitivity_incentive = []
    for incentive in incentive_list:
        performance_final_across_sensitivity = []
        consensus_final_across_sensitivity = []
        diversity_final_across_sensitivity = []
        variance_final_across_sensitivity = []
        for sensitivity in sensitivity_list:
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, incentive, sensitivity, active_rate, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.

            # remove the time dimension
            performance_across_repeat = [result[0][-1] for result in results]
            consensus_across_repeat = [result[1][-1] for result in results]
            diversity_across_repeat = [result[2][-1] for result in results]
            variance_across_repeat = [result[3][-1] for result in results]
            # After taking an average across repetitions
            performance_final = sum(performance_across_repeat) / len(performance_across_repeat)
            consensus_final = sum(consensus_across_repeat) / len(consensus_across_repeat)
            diversity_final = sum(diversity_across_repeat) / len(diversity_across_repeat)
            variance_final = sum(variance_across_repeat) / len(variance_across_repeat)

            performance_final_across_sensitivity.append(performance_final)
            consensus_final_across_sensitivity.append(consensus_final)
            diversity_final_across_sensitivity.append(diversity_final)
            variance_final_across_sensitivity.append(variance_final)

        performance_final_across_sensitivity_incentive.append(performance_final_across_sensitivity)
        consensus_final_across_sensitivity_incentive.append(consensus_final_across_sensitivity)
        diversity_final_across_sensitivity_incentive.append(diversity_final_across_sensitivity)
        variance_final_across_sensitivity_incentive.append(variance_final_across_sensitivity)

    index = 1
    while os.path.exists(r"dao_performance_2_{0}".format(index)):
        index += 1
    with open("dao_performance_2_{0}".format(index), 'wb') as out_file:
        pickle.dump(performance_final_across_sensitivity_incentive, out_file)
    with open("dao_consensus_performance_2_{0}".format(index), 'wb') as out_file:
        pickle.dump(consensus_final_across_sensitivity_incentive, out_file)
    with open("dao_diversity_2_{0}".format(index), 'wb') as out_file:
        pickle.dump(diversity_final_across_sensitivity_incentive, out_file)
    with open("dao_variance_2_{0}".format(index), 'wb') as out_file:
        pickle.dump(variance_final_across_sensitivity_incentive, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
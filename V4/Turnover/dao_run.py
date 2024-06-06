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
import os
import math


def func(m=None, n=None, group_size=None, lr=None, turnover_rate=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for period in range(search_loop):
        # Turbulence
        # if (period + 1) % 100 == 0:
        #     reality.change(reality_change_rate=0.1)
        #     for team in dao.teams:
        #         for individual in team.individuals:
        #             individual.payoff = reality.get_payoff(belief=individual.belief)
        # Turnover
        if turnover_rate != 0:
            dao.turnover(turnover_rate=turnover_rate)
        dao.search(threshold_ratio=0.5)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    turnover_rate_list = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
    group_size = 7
    n = 350
    lr = 0.3
    repetition = 50
    concurrency = 50
    search_loop = 300
    # DVs
    performance_across_para = []
    consensus_performance_across_para = []
    diversity_across_para = []
    variance_across_para = []

    # performance_across_para_time = []
    # diversity_across_para_time = []
    # consensus_performance_across_para_time = []
    # variance_across_para_time = []
    for turnover_rate in turnover_rate_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, n, group_size, lr, turnover_rate, search_loop, loop, return_dict, sema))
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
        # performance_across_repeat_time = [result[0] for result in results]
        # consensus_performance_across_repeat_time = [result[1] for result in results]
        # diversity_across_repeat_time = [result[2] for result in results]
        # variance_across_repeat_time = [result[3] for result in results]

        # take an average across repetition, for each time iteration, integrate into 600 values for one parameter
        # performance_across_time = []  # under the same parameter
        # consensus_performance_across_time = []
        # diversity_across_time = []
        # variance_across_time = []
        # for period in range(search_loop):
        #     temp_performance = [performance_list[period] for performance_list in performance_across_repeat_time]
        #     performance_across_time.append(sum(temp_performance) / len(temp_performance))
        #     temp_consensus_performance = [performance_list[period] for performance_list in
        #                                   consensus_performance_across_repeat_time]
        #     consensus_performance_across_time.append(sum(temp_consensus_performance) / len(temp_consensus_performance))
        #
        #     temp_diversity = [diversity_list[period] for diversity_list in diversity_across_repeat_time]
        #     diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))
        #
        #     temp_variance = [variance_list[period] for variance_list in variance_across_repeat_time]
        #     variance_across_time.append(sum(temp_variance) / len(temp_variance))

        # retain the time dimension
        # performance_across_para_time.append(performance_across_time)
        # consensus_performance_across_para_time.append(consensus_performance_across_time)
        # diversity_across_para_time.append(diversity_across_time)
        # variance_across_para_time.append(variance_across_time)

    # small tasks
    # =============================
    # delay = np.random.uniform(1, 6)
    # time.sleep(delay)
    # performance_file_name = "dao_performance_across_turnover_1"
    #
    # if os.path.exists(performance_file_name):
    #     with open("dao_performance_across_turnover_1", 'rb') as infile:
    #         prior_performance = pickle.load(infile)
    #     with open("dao_diversity_across_turnover_1", 'rb') as infile:
    #         prior_diversity = pickle.load(infile)
    #     with open("dao_variance_across_turnover_1", 'rb') as infile:
    #         prior_variance = pickle.load(infile)
    #     performance_final = [(each_1 + each_2) / 2 for each_1, each_2 in
    #                          zip(prior_performance, performance_across_para)]
    #     diversity_final = [(each_1 + each_2) / 2 for each_1, each_2 in zip(prior_diversity, diversity_across_para)]
    #     variance_final = [(each_1 + each_2) / 2 for each_1, each_2 in zip(prior_variance, variance_across_para)]
    #     with open("dao_performance_across_turnover_1", 'wb') as out_file:
    #         pickle.dump(performance_final, out_file)
    #     with open("dao_diversity_across_turnover_1", 'wb') as out_file:
    #         pickle.dump(diversity_final, out_file)
    #     with open("dao_variance_across_turnover_1", 'wb') as out_file:
    #         pickle.dump(variance_final, out_file)
    #
    # else:
    #     with open("dao_performance_across_turnover_1", 'wb') as out_file:
    #         pickle.dump(performance_across_para, out_file)
    #     with open("dao_diversity_across_turnover_1", 'wb') as out_file:
    #         pickle.dump(diversity_across_para, out_file)
    #     with open("dao_variance_across_turnover_1", 'wb') as out_file:
    #         pickle.dump(variance_across_para, out_file)
    # ==============================
    delay = np.random.uniform(10, 60)
    time.sleep(delay)
    index = 1
    performance_file_name = "dao_performance_across_turnover_{0}".format(index)
    while os.path.exists(performance_file_name):
        index += 1
        performance_file_name = "dao_performance_across_turnover_{0}".format(index)

    with open("dao_performance_across_turnover_{0}".format(index), 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("dao_diversity_across_turnover_{0}".format(index), 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("dao_variance_across_turnover_{0}".format(index), 'wb') as out_file:
        pickle.dump(variance_across_para, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))


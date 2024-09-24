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


def func(m=None, n=None, group_size=None, lr=None, incentive=None,
         active_rate=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    # pre-assign the token according to the asymmetry degree
    mode = 1
    # Fixing the asymmetry  !!!!!
    asymmetry = 0
    if asymmetry == 0:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = 1
    else:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = (np.random.pareto(a=asymmetry) + 1) * mode
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
    incentive_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    group_size = 7  # the smallest group size in Fang's model: 7

    concurrency = 50
    active_rate = 0.6
    # DVs
    performance_final_across_incentive = []
    consensus_final_across_incentive = []
    diversity_final_across_incentive = []
    variance_final_across_incentive = []

    performance_final_across_incentive_time = []
    consensus_final_across_incentive_time = []
    diversity_final_across_incentive_time = []
    variance_final_across_incentive_time = []
    for incentive in incentive_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, n, group_size, lr, incentive, active_rate, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.

        # keep the time dimension
        performance_across_repeat = [result[0] for result in results]
        consensus_across_repeat = [result[1] for result in results]
        diversity_across_repeat = [result[2] for result in results]
        variance_across_repeat = [result[3] for result in results]

        performance_across_time = []
        consensus_across_time = []
        diversity_across_time = []
        variance_across_time = []
        for period in range(search_loop):
            performance_temp = [each[period] for each in performance_across_repeat]
            performance_across_time.append(sum(performance_temp) / len(performance_temp))

            consensus_temp = [each[period] for each in consensus_across_repeat]
            consensus_across_time.append(sum(consensus_temp) / len(consensus_temp))

            diversity_temp = [each[period] for each in diversity_across_repeat]
            diversity_across_time.append(sum(diversity_temp) / len(diversity_temp))

            variance_temp = [each[period] for each in variance_across_repeat]
            variance_across_time.append(sum(variance_temp) / len(variance_temp))
        # remove the time dimension
        performance_final_across_incentive.append(performance_across_time[-1])
        consensus_final_across_incentive.append(consensus_across_time[-1])
        diversity_final_across_incentive.append(diversity_across_time[-1])
        variance_final_across_incentive.append(variance_across_time[-1])
        # keep the time dimension
        performance_final_across_incentive_time.append(performance_across_time)
        consensus_final_across_incentive_time.append(consensus_across_time)
        diversity_final_across_incentive_time.append(diversity_across_time)
        variance_final_across_incentive_time.append(variance_across_time)

    # Automatic integration of results
    time.sleep(np.random.uniform(low=2, high=60))
    if os.path.exists(r"dao_performance"):
        with open("dao_performance", 'rb') as infile:
            prior_results = pickle.load(infile)
            performance_final_across_incentive = [0.5 * (a + b) for a, b in zip(performance_final_across_incentive, prior_results)]
        with open("dao_consensus_performance", 'rb') as infile:
            prior_results = pickle.load(infile)
            consensus_final_across_incentive = [0.5 * (a + b) for a, b in zip(consensus_final_across_incentive, prior_results)]
        with open("dao_diversity", 'rb') as infile:
            prior_results = pickle.load(infile)
            diversity_final_across_incentive = [0.5 * (a + b) for a, b in zip(diversity_final_across_incentive, prior_results)]
        with open("dao_variance", 'rb') as infile:
            prior_results = pickle.load(infile)
            variance_final_across_incentive = [0.5 * (a + b) for a, b in zip(variance_final_across_incentive, prior_results)]

        with open("dao_performance_across_time", 'rb') as infile:
            prior_results = pickle.load(infile)
            for index, row_1, row_2 in zip(range(len(prior_results)), prior_results, performance_final_across_incentive_time):
                new_row = [0.5 * (a + b) for a, b in zip(row_1, row_2)]
                performance_final_across_incentive_time[index] = new_row
        with open("dao_consensus_performance_across_time", 'rb') as infile:
            prior_results = pickle.load(infile)
            for index, row_1, row_2 in zip(range(len(prior_results)), prior_results, consensus_final_across_incentive_time):
                new_row = [0.5 * (a + b) for a, b in zip(row_1, row_2)]
                consensus_final_across_incentive_time[index] = new_row
        with open("dao_diversity_across_time", 'rb') as infile:
            prior_results = pickle.load(infile)
            for index, row_1, row_2 in zip(range(len(prior_results)), prior_results, diversity_final_across_incentive_time):
                new_row = [0.5 * (a + b) for a, b in zip(row_1, row_2)]
                diversity_final_across_incentive_time[index] = new_row
        with open("dao_variance_across_time", 'rb') as infile:
            prior_results = pickle.load(infile)
            for index, row_1, row_2 in zip(range(len(prior_results)), prior_results, variance_final_across_incentive_time):
                new_row = [0.5 * (a + b) for a, b in zip(row_1, row_2)]
                variance_final_across_incentive_time[index] = new_row

    # remove time
    with open("dao_performance", 'wb') as out_file:
        pickle.dump(performance_final_across_incentive, out_file)
    with open("dao_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_final_across_incentive, out_file)
    with open("dao_diversity", 'wb') as out_file:
        pickle.dump(diversity_final_across_incentive, out_file)
    with open("dao_variance", 'wb') as out_file:
        pickle.dump(variance_final_across_incentive, out_file)
    # keep time
    with open("dao_performance_across_time", 'wb') as out_file:
        pickle.dump(performance_final_across_incentive_time, out_file)
    with open("dao_consensus_performance_across_time", 'wb') as out_file:
        pickle.dump(consensus_final_across_incentive_time, out_file)
    with open("dao_diversity_across_time", 'wb') as out_file:
        pickle.dump(diversity_final_across_incentive_time, out_file)
    with open("dao_variance_across_time", 'wb') as out_file:
        pickle.dump(variance_final_across_incentive_time, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
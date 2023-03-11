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


def func(m=None, s=None, n=None, group_size=None, lr=None, initialization_bar=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    autonomy = Autonomy(m=m, s=s, n=n, reality=reality, group_size=group_size, lr=lr)
    # initialization
    for team in autonomy.teams:
        for individual in team.individuals:
            bounded_payoff =  np.random.uniform(initialization_bar, initialization_bar+0.1)
            correct_num = math.ceil(bounded_payoff * m)
            correct_indexes = np.random.choice(range(m), correct_num, replace=False)
            for index in range(m):
                if index in correct_indexes:
                    individual.belief[index] = reality.real_code[index]
                else:
                    individual.belief[index] = np.random.choice((0, -1 * reality.real_code[index]))
            individual.payoff = reality.get_payoff(belief=individual.belief)
            individual.policy = reality.belief_2_policy(belief=individual.belief)  # a fake policy for voting
    for _ in range(search_loop):
        autonomy.search()
    return_dict[loop] = [autonomy.performance_across_time, autonomy.diversity_across_time, autonomy.variance_across_time,
                         autonomy.variance_across_time, autonomy.percentile_10_across_time, autonomy.percentile_90_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    initialization_bar_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    n = 350
    lr = 0.3
    repetition = 200
    concurrency = 50
    search_loop = 100
    group_size = 7  # the smallest group size in Fang's model: 7
    # DVs
    # after taking an average across repetitions
    performance_across_para = []
    consensus_across_para = []
    diversity_across_para = []
    variance_across_para = []
    percentile_10_across_para = []
    percentile_90_across_para = []
    # before taking an average across repetitions
    performance_hyper = []
    consensus_hyper = []
    diversity_hyper = []
    variance_hyper = []
    percentile_10_hyper = []
    percentile_90_hyper = []
    # retian the time dimension
    # before taking an average across repetitions
    performance_across_para_time = []
    consensus_across_para_time = []
    diversity_across_para_time = []
    variance_across_para_time = []
    percentile_10_across_para_time = []
    percentile_90_across_para_time = []
    for initialization_bar in initialization_bar_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, s, n, group_size, lr, initialization_bar, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.

        # remove the time dimension, only keep the last value
        performance_hyper += [result[0][-1] for result in results]
        diversity_hyper += [result[1][-1] for result in results]
        variance_hyper += [result[2][-1] for result in results]
        percentile_10_hyper += [result[3][-1] for result in results]
        percentile_90_hyper += [result[4][-1] for result in results]

        # take an average across repetition, only one value for one parameter
        performance_across_para.append(sum(performance_hyper) / len(performance_hyper))
        diversity_across_para.append(sum(diversity_hyper) / len(diversity_hyper))
        variance_across_para.append(sum(variance_hyper) / len(variance_hyper))
        percentile_10_across_para.append(sum(percentile_10_hyper) / len(percentile_10_hyper))
        percentile_90_across_para.append(sum(percentile_90_hyper) / len(percentile_90_hyper))

        # keep the time dimension
        performance_across_repeat_time = [result[0] for result in results]
        diversity_across_repeat_time = [result[1] for result in results]
        variance_across_repeat_time = [result[2] for result in results]
        percentile_10_across_repeat_time = [result[3] for result in results]
        percentile_90_across_repeat_time = [result[4] for result in results]

        # take an average across repetition, for each time iteration, integrate into [loop] values for one parameter
        performance_across_time = []  # under the same parameter
        diversity_across_time = []
        variance_across_time = []
        percentile_10_across_time = []
        percentile_90_across_time = []
        for period in range(search_loop):
            temp_performance = [performance_list[period] for performance_list in performance_across_repeat_time]
            performance_across_time.append(sum(temp_performance) / len(temp_performance))

            temp_diversity = [diversity_list[period] for diversity_list in diversity_across_repeat_time]
            diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))

            temp_variance = [variance_list[period] for variance_list in variance_across_repeat_time]
            variance_across_time.append(sum(temp_variance) / len(temp_variance))

            temp_percentile_10 = [percentile_10_list[period] for percentile_10_list in percentile_10_across_repeat_time]
            percentile_10_across_time.append(sum(temp_percentile_10) / len(temp_percentile_10))

            temp_percentile_90 = [percentile_90_list[period] for percentile_90_list in percentile_90_across_repeat_time]
            percentile_90_across_time.append(sum(temp_percentile_90) / len(temp_percentile_90))
        # retain the time dimension
        performance_across_para_time.append(performance_across_time)
        diversity_across_para_time.append(diversity_across_time)
        variance_across_para_time.append(variance_across_time)
        percentile_10_across_para_time.append(percentile_10_across_time)
        percentile_90_across_para_time.append(percentile_90_across_time)

    # save the without-time data
    with open("autonomy_performance_across_z", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("autonomy_diversity_across_z", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("autonomy_variance_across_z", 'wb') as out_file:
        pickle.dump(variance_across_para, out_file)
    with open("autonomy_percentile_10_across_z", 'wb') as out_file:
        pickle.dump(percentile_10_across_para, out_file)
    with open("autonomy_percentile_90_across_z", 'wb') as out_file:
        pickle.dump(percentile_90_across_para, out_file)

    # save the with-time data
    with open("autonomy_performance_across_z_time", 'wb') as out_file:
        pickle.dump(performance_across_para_time, out_file)
    with open("autonomy_diversity_across_z_time", 'wb') as out_file:
        pickle.dump(diversity_across_para_time, out_file)
    with open("autonomy_variance_across_z_time", 'wb') as out_file:
        pickle.dump(variance_across_para_time, out_file)
    with open("autonomy_percentile_10_across_z_time", 'wb') as out_file:
        pickle.dump(percentile_10_across_para_time, out_file)
    with open("autonomy_percentile_10_across_z_time", 'wb') as out_file:
        pickle.dump(percentile_90_across_para_time, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
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


def func(m=None, s=None, n=None, group_size=None, lr=None, asymmetry=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    mode = 10
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size)
    # pre-assign the token according to the asymmetry degree
    if asymmetry == 0:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = 1
    else:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = (np.random.pareto(a=asymmetry) + 1) * mode

        # calculate the Gini index of the generated token
        token_list = []
        for team in dao.teams:
            token_list += [individual.token for individual in team.individuals]
        gini_coef = gini(array=token_list)
        print("Asymmetry={0}, Gini={1}".format(asymmetry, gini_coef))
    for period in range(search_loop):
        dao.search(threshold_ratio=0.5, token=True, incentive=False)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time, dao.percentile_10_across_time,
                         dao.percentile_90_across_time]
    sema.release()


def gini(array):
    array = sorted(array)
    n = len(array)
    coefficient = 0
    for i, value in enumerate(array):
        coefficient += (2 * i + 1) * value
    coefficient /= n * sum(array)
    coefficient -= (n + 1) / n
    return coefficient

if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 350
    lr = 0.3
    hyper_iteration = 20
    repetition = 50
    search_loop = 100
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 50
    asymmetry_list = [0, 1, 2, 3]  # smaller asymmetry is associated with higher wealth inequality
    # after taking an average across repetitions
    performance_across_para = []
    consensus_across_para = []
    diversity_across_para = []
    variance_across_para = []
    percentile_10_across_para = []
    percentile_90_across_para = []
    # before taking an average across repetitions
    performance_across_para_hyper = []
    consensus_across_para_hyper = []
    diversity_across_para_hyper = []
    variance_across_para_hyper = []
    percentile_10_across_para_hyper = []
    percentile_90_across_para_hyper = []
    for asymmetry in asymmetry_list:
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
                               args=(m, s, n, group_size, lr, asymmetry, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.
            performance_hyper += [result[0] for result in results]
            consensus_hyper += [result[1] for result in results]
            diversity_hyper += [result[2] for result in results]
            variance_hyper += [result[3] for result in results]
            percentile_10_hyper += [result[4] for result in results]
            percentile_90_hyper += [result[5] for result in results]
        for period in range(search_loop):
            performance_temp = [performance_list[period] for performance_list in performance_hyper]
            consensus_temp = [consensus_list[period] for consensus_list in consensus_hyper]
            diversity_temp = [diversity_list[period] for diversity_list in diversity_hyper]
            variance_temp = [variance_list[period] for variance_list in variance_hyper]
            percentile_10_temp = [percentile_10_list[period] for percentile_10_list in percentile_10_hyper]
            percentile_90_temp = [percentile_90_list[period] for percentile_90_list in percentile_90_hyper]

            performance_final.append(sum(performance_temp) / len(performance_temp))
            consensus_final.append(sum(consensus_temp) / len(consensus_temp))
            diversity_final.append(sum(diversity_temp) / len(diversity_temp))
            variance_final.append(sum(variance_temp) / len(variance_temp))
            percentile_10_final.append(sum(percentile_10_temp) / len(percentile_10_temp))
            percentile_90_final.append(sum(percentile_90_temp) / len(percentile_90_temp))

        # after taking an average (ready for figure)
        performance_across_para.append(performance_final)
        consensus_across_para.append(consensus_final)
        diversity_across_para.append(diversity_final)
        variance_across_para.append(variance_final)
        percentile_10_across_para.append(percentile_10_final)
        percentile_90_across_para.append(percentile_90_final)

        # before taking an average
        performance_across_para_hyper.append(performance_hyper)
        consensus_across_para_hyper.append(consensus_hyper)
        diversity_across_para_hyper.append(diversity_hyper)
        variance_across_para_hyper.append(variance_hyper)
        percentile_10_across_para_hyper.append(percentile_10_hyper)
        percentile_90_across_para_hyper.append(percentile_90_hyper)

    # after taking an average across repetitions
    with open("dao_performance", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("dao_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para, out_file)
    with open("dao_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("dao_variance", 'wb') as out_file:
        pickle.dump(variance_across_para, out_file)
    with open("dao_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_across_para, out_file)
    with open("dao_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_across_para, out_file)

    # before taking an average across repetitions
    with open("dao_original_performance", 'wb') as out_file:
        pickle.dump(performance_across_para_hyper, out_file)
    with open("dao_original_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para_hyper, out_file)
    with open("dao_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para_hyper, out_file)
    with open("dao_original_variance", 'wb') as out_file:
        pickle.dump(variance_across_para_hyper, out_file)
    with open("dao_original_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_across_para_hyper, out_file)
    with open("dao_original_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_across_para_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

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


def func(m=None, s=None, n=None, group_size=None, lr=None, incentive=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size)
    # initially with equal token
    for team in dao.teams:
        for individual in team.individuals:
            individual.token = 1
    if incentive == 0:
        for _ in range(search_loop):
            dao.search(threshold_ratio=0.5)
    else:
        for _ in range(search_loop):
            dao.incentive_search(threshold_ratio=0.5, incentive=incentive)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time, dao.gini_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 350
    lr = 0.3
    hyper_iteration = 10
    repetition = 50
    incentive_list = [0, 1, 10, 100]
    search_loop = 500
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 50
    # DVs
    performance_across_para = []
    consensus_across_para = []
    diversity_across_para = []
    variance_across_para = []
    gini_across_para = []

    performance_across_para_hyper = []
    consensus_across_para_hyper = []
    diversity_across_para_hyper = []
    variance_across_para_hyper = []
    gini_across_para_hyper = []
    for incentive in incentive_list:
        # before taking an average across repetitions
        performance_across_hyper = []
        consensus_across_hyper = []
        diversity_across_hyper = []
        variance_across_hyper = []
        gini_across_hyper = []

        # after taking an average across repetitions
        performance_final = []
        consensus_final = []
        diversity_final = []
        variance_final = []
        gini_final = []

        for hyper_loop in range(hyper_iteration):
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, s, n, group_size, lr, incentive, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.
            performance_across_hyper += [result[0] for result in results]
            consensus_across_hyper += [result[1] for result in results]
            diversity_across_hyper += [result[2] for result in results]
            variance_across_hyper += [result[3] for result in results]
            gini_across_hyper += [result[4] for result in results]
        for period in range(search_loop):
            performance_temp = [performance_list[period] for performance_list in performance_across_hyper]
            consensus_temp = [consensus_list[period] for consensus_list in consensus_across_hyper]
            diversity_temp = [diversity_list[period] for diversity_list in diversity_across_hyper]
            variance_temp = [variance_list[period] for variance_list in variance_across_hyper]
            gini_temp = [gini_list[period] for gini_list in gini_across_hyper]

            performance_final.append(sum(performance_temp) / len(performance_temp))
            consensus_final.append(sum(consensus_temp) / len(consensus_temp))
            diversity_final.append(sum(diversity_temp) / len(diversity_temp))
            variance_final.append(sum(variance_temp) / len(variance_temp))
            gini_final.append(sum(gini_temp) / len(gini_temp))

        # after taking an average (ready for figure)
        performance_across_para.append(performance_final)
        consensus_across_para.append(consensus_final)
        diversity_across_para.append(diversity_final)
        variance_across_para.append(variance_final)
        gini_across_para.append(gini_final)

        # before taking an average
        performance_across_para_hyper.append(performance_across_hyper)
        consensus_across_para_hyper.append(consensus_across_hyper)
        diversity_across_para_hyper.append(diversity_across_hyper)
        variance_across_para_hyper.append(variance_across_hyper)
        gini_across_para_hyper.append(gini_across_hyper)

    with open("dao_performance", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("dao_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para, out_file)
    with open("dao_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("dao_variance", 'wb') as out_file:
        pickle.dump(variance_across_para, out_file)
    with open("dao_gini", 'wb') as out_file:
        pickle.dump(gini_across_para, out_file)

    with open("dao_original_performance", 'wb') as out_file:
        pickle.dump(performance_across_para_hyper, out_file)
    with open("dao_original_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para_hyper, out_file)
    with open("dao_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para_hyper, out_file)
    with open("dao_original_variance", 'wb') as out_file:
        pickle.dump(variance_across_para_hyper, out_file)
    with open("dao_original_gini", 'wb') as out_file:
        pickle.dump(gini_across_para_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
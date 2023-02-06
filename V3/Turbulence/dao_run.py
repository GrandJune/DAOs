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


def func(m=None, s=None, n=None, group_size=None, lr=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size)
    for period in range(search_loop):
        # Christina Fang use a regular turbulence in her paper; This periodic turbulence suggest that hierarchy out-perform DAO in our previous results
        # Thus we try a more random turbulence;
        if (period + 1) % 100 == 0:
            reality.change(reality_change_rate=0.1)
            for team in dao.teams:
                for individual in team.individuals:
                    individual.payoff = reality.get_payoff(belief=individual.belief)
        for team in dao.teams:
            for individual in team.individuals:
                individual.payoff = reality.get_payoff(belief=individual.belief)
        dao.search(threshold_ratio=0.5)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time, dao.percentile_10_across_time,
                         dao.percentile_90_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 350
    lr = 0.3
    hyper_iteration = 4
    repetition = 50
    search_loop = 2000
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 50
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
                           args=(m, s, n, group_size, lr, search_loop, loop, return_dict, sema))
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
        temp_variance = sum([result[period] for result in variance_hyper]) / len(variance_hyper)
        temp_percentile_10 = sum([result[period] for result in percentile_10_hyper]) / len(percentile_10_hyper)
        temp_percentile_90 = sum([result[period] for result in percentile_90_hyper]) / len(percentile_90_hyper)

        performance_final.append(sum(performance_temp) / len(performance_temp))
        consensus_final.append(sum(consensus_temp) / len(consensus_temp))
        diversity_final.append(sum(diversity_temp) / len(diversity_temp))
        variance_final.append(temp_variance)
        percentile_10_final.append(temp_percentile_10)
        percentile_90_final.append(temp_percentile_90)

    # after taking an average across repetitions
    with open("dao_performance", 'wb') as out_file:
        pickle.dump(performance_final, out_file)
    with open("dao_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_final, out_file)
    with open("dao_diversity", 'wb') as out_file:
        pickle.dump(diversity_final, out_file)
    with open("dao_variance", 'wb') as out_file:
        pickle.dump(variance_final, out_file)
    with open("dao_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_final, out_file)
    with open("dao_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_final, out_file)

    # before taking an average across repetitions
    with open("dao_original_performance", 'wb') as out_file:
        pickle.dump(performance_hyper, out_file)
    with open("dao_original_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_hyper, out_file)
    with open("dao_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_hyper, out_file)
    with open("dao_original_variance", 'wb') as out_file:
        pickle.dump(variance_hyper, out_file)
    with open("dao_original_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_hyper, out_file)
    with open("dao_original_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))


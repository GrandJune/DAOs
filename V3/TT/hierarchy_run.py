# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: hierarchy_run.py
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


def func(m=None, s=None, n=None, group_size=None, lr=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    hierarchy = Hierarchy(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size, p1=0.1, p2=0.9)
    for period in range(search_loop):
        # Turbulence first
        if (period + 1) % 100 == 0:
            reality.change(reality_change_rate=0.1)
            # update the individual payoff
            for team in hierarchy.teams:
                for individual in team.individuals:
                    individual.payoff = reality.get_payoff(belief=individual.belief)
            # update the manager payoff
            for manager in hierarchy.superior.managers:
                manager.payoff = reality.get_policy_payoff(policy=manager.policy)
            # update the code payoff
            hierarchy.superior.code_payoff = reality.get_policy_payoff(policy=hierarchy.superior.code)
        # Then turnover
        hierarchy.turnover(turnover_rate=0.1)
        hierarchy.search()
    return_dict[loop] = [hierarchy.performance_across_time, hierarchy.superior.performance_average_across_time,
                         hierarchy.diversity_across_time, hierarchy.variance_across_time,
                         hierarchy.percentile_10_across_time, hierarchy.percentile_90_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 350
    lr = 0.3
    hyper_iteration = 10
    repetition = 50
    search_loop = 1000
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
        variance_temp = [variance_list[period] for variance_list in variance_hyper]
        percentile_10_temp = [percentile_10_list[period] for percentile_10_list in percentile_10_hyper]
        percentile_90_temp = [percentile_90_list[period] for percentile_90_list in percentile_90_hyper]

        performance_final.append(sum(performance_temp) / len(performance_temp))
        consensus_final.append(sum(consensus_temp) / len(consensus_temp))
        diversity_final.append(sum(diversity_temp) / len(diversity_temp))
        variance_final.append(sum(variance_temp) / len(variance_temp))
        percentile_10_final.append(sum(percentile_10_temp) / len(percentile_10_temp))
        percentile_90_final.append(sum(percentile_90_temp) / len(percentile_90_temp))

    # after taking an average across repetitions
    with open("hierarchy_performance", 'wb') as out_file:
        pickle.dump(performance_final, out_file)
    with open("hierarchy_superior_performance", 'wb') as out_file:
        pickle.dump(consensus_final, out_file)
    with open("hierarchy_diversity", 'wb') as out_file:
        pickle.dump(diversity_final, out_file)
    with open("hierarchy_variance", 'wb') as out_file:
        pickle.dump(variance_final, out_file)
    with open("hierarchy_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_final, out_file)
    with open("hierarchy_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_final, out_file)

    # before taking an average across repetitions
    with open("hierarchy_original_performance", 'wb') as out_file:
        pickle.dump(performance_hyper, out_file)
    with open("hierarchy_original_superior_performance", 'wb') as out_file:
        pickle.dump(consensus_hyper, out_file)
    with open("hierarchy_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_hyper, out_file)
    with open("hierarchy_original_variance", 'wb') as out_file:
        pickle.dump(variance_hyper, out_file)
    with open("hierarchy_original_percentile_10", 'wb') as out_file:
        pickle.dump(percentile_10_hyper, out_file)
    with open("hierarchy_original_percentile_90", 'wb') as out_file:
        pickle.dump(percentile_90_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
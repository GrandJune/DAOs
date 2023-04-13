# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO import DAO
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Pool
from multiprocessing import Semaphore
import pickle
import math


def func(m=None, s=None, n=None, group_size=None, lr=None, incentive=None, inactive_rate=None,
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
            dao.incentive_search(threshold_ratio=0.5, incentive=incentive, inactive_rate=inactive_rate)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time, dao.gini_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 1
    n = 350
    lr = 0.3
    repetition = 200
    incentive_list = [0.5, 0.6]
    inactive_rate_list = [0, 0.1, 0.2, 0.3, 0.4]
    search_loop = 500
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 50
    for incentive in incentive_list:
        for inactive_rate in inactive_rate_list:
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, s, n, group_size, lr, incentive, inactive_rate, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.
            performance_across_repeat = [result[0] for result in results]
            consensus_across_repeat = [result[1] for result in results]
            diversity_across_repeat = [result[2] for result in results]
            variance_across_repeat = [result[3] for result in results]
            gini_across_repeat = [result[4] for result in results]
            # After taking an average across repetitions
            performance_final = []
            consensus_final = []
            diversity_final = []
            variance_final = []
            gini_final = []
            for period in range(search_loop):
                performance_temp = [performance_list[period] for performance_list in performance_across_repeat]
                consensus_temp = [consensus_list[period] for consensus_list in consensus_across_repeat]
                diversity_temp = [diversity_list[period] for diversity_list in diversity_across_repeat]
                variance_temp = [variance_list[period] for variance_list in variance_across_repeat]
                gini_temp = [gini_list[period] for gini_list in gini_across_repeat]

                performance_final.append(sum(performance_temp) / len(performance_temp))
                consensus_final.append(sum(consensus_temp) / len(consensus_temp))
                diversity_final.append(sum(diversity_temp) / len(diversity_temp))
                variance_final.append(sum(variance_temp) / len(variance_temp))
                gini_final.append(sum(gini_temp) / len(gini_temp))

            with open("dao_performance_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(performance_final, out_file)
            with open("dao_consensus_performance_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(consensus_final, out_file)
            with open("dao_diversity_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(diversity_final, out_file)
            with open("dao_variance_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(variance_final, out_file)
            with open("dao_gini_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(gini_final, out_file)

            with open("dao_original_performance_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(performance_across_repeat, out_file)
            with open("dao_original_consensus_performance_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(consensus_across_repeat, out_file)
            with open("dao_original_diversity_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(diversity_across_repeat, out_file)
            with open("dao_original_variance_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(variance_across_repeat, out_file)
            with open("dao_original_gini_incentive_{0}_inactive_{1}".format(incentive, inactive_rate), 'wb') as out_file:
                pickle.dump(gini_across_repeat, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
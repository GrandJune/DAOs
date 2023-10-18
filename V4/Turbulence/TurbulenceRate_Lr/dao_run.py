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
from multiprocessing import Semaphore
import pickle
# import math


def func(m=None, n=None, group_size=None, lr=None, turbulence_freq=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    for period in range(search_loop):
        if (period + 1) % turbulence_freq == 0:
            reality.change(reality_change_rate=0.15)
            for team in dao.teams:
                for individual in team.individuals:
                    individual.payoff = reality.get_payoff(belief=individual.belief)
        dao.search(threshold_ratio=0.5)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    turbulence_freq_list = [20, 40, 60, 80, 100]
    group_size = 7
    n = 350
    lr_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    repetition = 200
    concurrency = 50
    search_loop = 1000
    for lr in lr_list:
        for turbulence_freq in turbulence_freq_list:
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, turbulence_freq, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.
            # keep the time dimension
            performance_across_repeat_time = [result[0] for result in results]
            consensus_performance_across_repeat_time = [result[1] for result in results]
            diversity_across_repeat_time = [result[2] for result in results]
            variance_across_repeat_time = [result[3] for result in results]

            performance_across_time = []
            consensus_performance_across_time = []
            diversity_across_time = []
            variance_across_time = []
            for period in range(search_loop):
                temp_performance = [performance_list[period] for performance_list in performance_across_repeat_time]
                performance_across_time.append(sum(temp_performance) / len(temp_performance))

                temp_consensus_performance = [performance_list[period] for performance_list in
                                              consensus_performance_across_repeat_time]
                consensus_performance_across_time.append(sum(temp_consensus_performance) / len(temp_consensus_performance))

                temp_diversity = [diversity_list[period] for diversity_list in diversity_across_repeat_time]
                diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))

                temp_variance = [variance_list[period] for variance_list in variance_across_repeat_time]
                variance_across_time.append(sum(temp_variance) / len(temp_variance))

            # save the with-time data
            with open("dao_performance_across_time_freq_{}_lr_{}".format(turbulence_freq, lr), 'wb') as out_file:
                pickle.dump(performance_across_time, out_file)
            with open("dao_consensus_across_time_freq_{}_lr_{}".format(turbulence_freq, lr), 'wb') as out_file:
                pickle.dump(consensus_performance_across_time, out_file)
            with open("dao_diversity_across_time_freq_{}_lr_{}".format(turbulence_freq, lr), 'wb') as out_file:
                pickle.dump(diversity_across_time, out_file)
            with open("dao_variance_across_time_freq_{}_lr_{}".format(turbulence_freq, lr), 'wb') as out_file:
                pickle.dump(variance_across_time, out_file)

    t1 = time.time()
    print("DAO: ", time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))


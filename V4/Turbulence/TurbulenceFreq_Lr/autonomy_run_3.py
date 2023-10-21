# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: autonomy_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Autonomy import Autonomy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle


def func(m=None, n=None, group_size=None, lr=None, turbulence_freq=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    autonomy = Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr)
    for period in range(search_loop):
        if (period + 1) % turbulence_freq == 0:
            reality.change(reality_change_rate=0.15)
            for team in autonomy.teams:
                for individual in team.individuals:
                    individual.payoff = reality.get_payoff(belief=individual.belief)
        autonomy.search()
    return_dict[loop] = [autonomy.performance_across_time, autonomy.diversity_across_time,
                         autonomy.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    turbulence_freq_list = [20, 40, 60, 80, 100]
    group_size = 7
    n = 350
    lr_list = [0.5, 0.6]
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
            diversity_across_repeat_time = [result[1] for result in results]
            variance_across_repeat_time = [result[2] for result in results]

            performance_across_time = []
            diversity_across_time = []
            variance_across_time = []
            for period in range(search_loop):
                temp_performance = [performance_list[period] for performance_list in performance_across_repeat_time]
                performance_across_time.append(sum(temp_performance) / len(temp_performance))

                temp_diversity = [diversity_list[period] for diversity_list in diversity_across_repeat_time]
                diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))

                temp_variance = [variance_list[period] for variance_list in variance_across_repeat_time]
                variance_across_time.append(sum(temp_variance) / len(temp_variance))

            # save the with-time data
            with open("autonomy_performance_across_time_freq_{}_lr_{}".format(turbulence_freq, lr), 'wb') as out_file:
                pickle.dump(performance_across_time, out_file)
            with open("autonomy_diversity_across_time_freq_{}_lr_{}".format(turbulence_freq, lr), 'wb') as out_file:
                pickle.dump(diversity_across_time, out_file)
            with open("autonomy_variance_across_time_freq_{}_lr_{}".format(turbulence_freq, lr), 'wb') as out_file:
                pickle.dump(variance_across_time, out_file)

    t1 = time.time()
    print("Autonomy: ", time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
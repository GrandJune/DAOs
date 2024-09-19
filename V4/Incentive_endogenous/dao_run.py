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


def func(m=None, n=None, group_size=None, lr=None, incentive=None, sensitivity=None,
         active_rate=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, sensitivity=sensitivity)
    # Initialized with equal token
    for team in dao.teams:
        for individual in team.individuals:
            individual.token = 1
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
    repetition = 400
    search_loop = 300
    incentive_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # * 9
    active_rate_list = [0.9, 0.8, 0.7, 0.6, 0.5]  # * 5
    sensitivity_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # * 9
    group_size = 7  # the smallest group size in Fang's model: 7

    concurrency = 50
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []

    active_rate = 0.7
    for incentive in incentive_list:
        for sensitivity in sensitivity_list:
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, incentive, sensitivity, active_rate, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.

            performance_across_repeat = [result[0] for result in results]
            consensus_across_repeat = [result[1] for result in results]
            diversity_across_repeat = [result[2] for result in results]
            variance_across_repeat = [result[3] for result in results]
            # After taking an average across repetitions
            performance_final = []
            consensus_final = []
            diversity_final = []
            variance_final = []
            for period in range(search_loop):
                performance_temp = [performance_list[period] for performance_list in performance_across_repeat]
                consensus_temp = [consensus_list[period] for consensus_list in consensus_across_repeat]
                diversity_temp = [diversity_list[period] for diversity_list in diversity_across_repeat]
                variance_temp = [variance_list[period] for variance_list in variance_across_repeat]

                performance_final.append(sum(performance_temp) / len(performance_temp))
                consensus_final.append(sum(consensus_temp) / len(consensus_temp))
                diversity_final.append(sum(diversity_temp) / len(diversity_temp))
                variance_final.append(sum(variance_temp) / len(variance_temp))

            performance_file_name = r"dao_performance_incentive_{0}_sensitivity_{1}".format(incentive, sensitivity)
            delay = np.random.uniform(1, 20)
            time.sleep(delay)
            if os.path.exists(performance_file_name):
                with open("dao_performance_incentive_{0}_sensitivity_{1}".format(incentive, sensitivity),
                          'rb') as infile:
                    prior_performance = pickle.load(infile)
                with open("dao_consensus_performance_incentive_{0}_sensitivity_{1}".format(incentive, sensitivity),
                          'wb') as infile:
                    prior_consensus = pickle.load(infile)
                with open("dao_diversity_incentive_{0}_sensitivity_{1}".format(incentive, sensitivity),
                          'wb') as infile:
                    prior_diversity = pickle.load(infile)
                with open("dao_variance_incentive_{0}_sensitivity_{1}".format(incentive, sensitivity), 'wb') as infile:
                    prior_variance = pickle.load(infile)
                performance_final = [(each_1 + each_2) / 2 for each_1, each_2 in
                                     zip(prior_performance, performance_final)]
                consensus_final = [(each_1 + each_2) / 2 for each_1, each_2 in
                                   zip(prior_consensus, consensus_final)]
                diversity_final = [(each_1 + each_2) / 2 for each_1, each_2 in
                                   zip(prior_diversity, diversity_final)]
                variance_final = [(each_1 + each_2) / 2 for each_1, each_2 in zip(prior_variance, variance_final)]
                with open("dao_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate),
                          'wb') as out_file:
                    pickle.dump(performance_final, out_file)
                with open("dao_consensus_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate),
                          'wb') as out_file:
                    pickle.dump(consensus_final, out_file)
                with open("dao_diversity_incentive_{0}_inactive_{1}".format(incentive, active_rate),
                          'wb') as out_file:
                    pickle.dump(diversity_final, out_file)
                with open("dao_variance_incentive_{0}_inactive_{1}".format(incentive, active_rate),
                          'wb') as out_file:
                    pickle.dump(variance_final, out_file)

            else:
                with open("dao_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate),
                          'wb') as out_file:
                    pickle.dump(performance_final, out_file)
                with open("dao_consensus_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate),
                          'wb') as out_file:
                    pickle.dump(consensus_final, out_file)
                with open("dao_diversity_incentive_{0}_inactive_{1}".format(incentive, active_rate),
                          'wb') as out_file:
                    pickle.dump(diversity_final, out_file)
                with open("dao_variance_incentive_{0}_inactive_{1}".format(incentive, active_rate),
                          'wb') as out_file:
                    pickle.dump(variance_final, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
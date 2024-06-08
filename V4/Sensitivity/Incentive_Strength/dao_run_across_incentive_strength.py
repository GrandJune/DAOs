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


def func(m=None, n=None, group_size=None, lr=None, incentive=None, incentive_strength=None, active_rate=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    # initially with equal token
    for team in dao.teams:
        for individual in team.individuals:
            individual.token = 1
    if incentive == 0:
        for _ in range(search_loop):
            dao.search(threshold_ratio=0.5)
    else:
        for _ in range(search_loop):
            new_consensus = []
            individuals = []
            for team in dao.teams:
                individuals += team.individuals
            for individual in individuals:
                individual.policy = reality.belief_2_policy(belief=individual.belief)
            for individual in individuals:
                if np.random.uniform(0, 1) < active_rate:  # if active rate, e.g., 0.8
                    individual.active = 1
                else:
                    if np.random.uniform(0, 1) < incentive:  # if incentive into vote, e.g., 0.8
                        individual.active = 1
                    else:
                        individual.active = 0
            threshold = 0.5 * sum([individual.token for individual in individuals])
            # consider the active status
            for i in range(m // 3):
                overall_sum = sum(
                    [individual.policy[i] * individual.token * individual.active for individual in individuals])
                positive_count = sum([individual.token for individual in individuals if
                                      (individual.policy[i] == 1) and (individual.active == 1)])
                negative_count = sum([individual.token for individual in individuals if
                                      (individual.policy[i] == -1) and (individual.active == 1)])
                if (positive_count > threshold) and overall_sum > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and overall_sum < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)
            # Once there is a change in consensus, reward the contributor
            for old_bit, new_bit, index in zip(dao.consensus, new_consensus, m // 3):
                if old_bit != new_bit:
                    for individual in individuals:
                        if (individual.policy[index] == new_bit) and (
                                individual.active == 1):  # individual active and vote correctly
                            individual.token += incentive_strength   # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            dao.consensus = new_consensus.copy()
            dao.consensus_payoff = reality.get_policy_payoff(policy=new_consensus)
            # 1) Generate and 2) adjust the superior majority view and 3) learn from it
            for team in dao.teams:
                team.form_individual_majority_view()
                team.adjust_majority_view_2_consensus(policy=dao.consensus)
                team.learn()
            performance_list = []
            for team in dao.teams:
                performance_list += [individual.payoff for individual in team.individuals]

            dao.performance_across_time.append(sum(performance_list) / len(performance_list))
            dao.variance_across_time.append(np.std(performance_list))
            dao.diversity_across_time.append(dao.get_diversity())
            dao.consensus_performance_across_time.append(dao.consensus_payoff)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time, dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    import os
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    repetition = 50
    incentive_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    active_rate = 0.8
    incentive_strength_list = [1, 5, 10, 20, 40]
    search_loop = 400
    group_size = 7
    concurrency = 50
    for incentive in incentive_list:
        performance_across_para, diversity_across_para, variance_across_para = [], [], []
        for incentive_strength in incentive_strength_list:
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, incentive, incentive_strength, active_rate, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.
            performance_across_repeat = [result[0][-1] for result in results]
            consensus_across_repeat = [result[1][-1] for result in results]
            diversity_across_repeat = [result[2][-1] for result in results]
            variance_across_repeat = [result[3][-1] for result in results]
            # After taking an average across repetitions
            performance_across_para.append(sum(performance_across_repeat) / len(performance_across_repeat))
            diversity_across_para.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
            variance_across_para.append(sum(variance_across_repeat) / len(variance_across_repeat))

        delay = np.random.uniform(1, 60)
        time.sleep(delay)
        index = 1
        performance_file_name = r"dao_performance_across_strength_incentive_{0}_{1}".format(incentive, index)
        while os.path.exists(performance_file_name):
            index += 1
            performance_file_name = r"dao_performance_across_strength_incentive_{0}_{1}".format(incentive, index)

        with open("dao_performance_across_strength_incentive_{0}_{1}".format(incentive, index), 'wb') as out_file:
            pickle.dump(performance_across_para, out_file)
        with open("dao_diversity_across_strength_incentive_{0}_{1}".format(incentive, index), 'wb') as out_file:
            pickle.dump(diversity_across_para, out_file)
        with open("dao_variance_across_strength_incentive_{0}_{1}".format(incentive, index), 'wb') as out_file:
            pickle.dump(variance_across_para, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
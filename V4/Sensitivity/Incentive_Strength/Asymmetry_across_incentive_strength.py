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
    # After search, save the gini and the token distribution
    gini_coefficient = dao.get_gini()
    token_distribution = []
    for team in dao.teams:
        token_distribution += [individual.token for individual in team.individuals]
    sorted_token_distribution = sorted(token_distribution)
    return_dict[loop] = [gini_coefficient, sorted_token_distribution]
    sema.release()


if __name__ == '__main__':
    import os
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    repetition = 50
    incentive = 0.5
    active_rate = 0.8
    incentive_strength_list = [1, 5, 10, 20, 40]
    search_loop = 400
    group_size = 7
    concurrency = 50
    gini_across_para, token_distribution_across_para = [], []
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
        gini_across_repeat = [result[0] for result in results]
        token_distribution_across_repeat = [result[1] for result in results]

        # After taking an average across repetitions
        gini_across_para.append(sum(gini_across_repeat) / len(gini_across_repeat))
        temp = []
        for index in range(len(token_distribution_across_repeat[0])):
            temp.append(sum([each[index] for each in token_distribution_across_repeat]) / len(token_distribution_across_repeat))
        token_distribution_across_para.append(temp)

    delay = np.random.uniform(1, 60)
    time.sleep(delay)
    index = 1
    gini_file_name = r"gini_across_strength_{0}".format(index)
    while os.path.exists(gini_file_name):
        index += 1
        gini_file_name = r"gini_across_strength_{0}".format(index)

    with open("gini_across_strength_{0}".format(index), 'wb') as out_file:
        pickle.dump(gini_across_para, out_file)
    with open("token_distribution_across_strength_{0}".format(index), 'wb') as out_file:
        pickle.dump(token_distribution_across_para, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
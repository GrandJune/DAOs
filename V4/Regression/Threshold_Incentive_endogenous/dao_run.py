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


def func(m=None, n=None, group_size=None, lr=None, incentive=None, active_rate=None, asymmetry=None,
         threshold_ratio=None, turbulence_freq=None, turbulence_level=None, search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    # pre-assign the token according to the asymmetry degree
    mode = 1

    if asymmetry == 0:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = 1
        token_sum_base = n
    else:
        token_sum_base = 0
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = (np.random.pareto(a=asymmetry) + 1) * mode
                token_sum_base += individual.token

    real_active_rate_list = []
    for period in range(search_loop):
        if (period + 1) % turbulence_freq == 0:
            reality.change(reality_change_rate=turbulence_level)
            for team in dao.teams:
                for individual in team.individuals:
                    individual.payoff = reality.get_payoff(belief=individual.belief)
        dao.incentive_search(threshold_ratio=threshold_ratio, incentive=incentive, basic_active_rate=active_rate, k=1)

        # update the real participant rate
        active_count = 0
        for team in dao.teams:
            active_count += sum([individual.active for individual in team.individuals])
        real_active_rate_list.append(active_count / n)

    # average active rate over time
    real_active_rate = sum(real_active_rate_list) / len(real_active_rate_list)
    gini = dao.get_gini()
    performance = dao.performance_across_time[-1]
    return_dict[loop] = [performance, incentive, active_rate, real_active_rate,
                         threshold_ratio, turbulence_freq, turbulence_level, lr, gini, asymmetry]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    np.random.seed(None)
    m = 90
    n = 350
    lr = 0.3
    repetition = 100
    search_loop = 300
    threshold_ratio_list = np.arange(0.40, 0.71, 0.01)  # 31 cases
    incentive_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    active_rate_list = [0.5, 0.6, 0.7, 0.8, 0.9]
    asymmetry_list = [1, 2, 3, 4]
    lr_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    group_size = 7  # the smallest group size in Fang's model: 7

    concurrency = 100
    sema = Semaphore(concurrency)
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition):
        incentive = np.random.choice(incentive_list)
        active_rate = np.random.choice(active_rate_list)
        threshold_ratio = np.random.choice(threshold_ratio_list)
        asymmetry = np.random.choice(asymmetry_list)
        lr = np.random.choice(lr_list)
        turbulence_freq = np.random.choice([20, 40, 60, 80, 100])
        turbulence_level = np.random.choice([0.10, 0.12, 0.14, 0.16, 0.18, 0.20])
        sema.acquire()
        p = mp.Process(target=func,
                       args=(m, n, group_size, lr, incentive, active_rate, asymmetry, threshold_ratio,
                             turbulence_freq, turbulence_level, search_loop, loop, return_dict, sema))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    results = return_dict.values()  # Don't need dict index, since it is repetition.
    # Automatic integration of results
    time.sleep(np.random.uniform(low=1, high=60))
    if os.path.exists("dao_data"):
        with open("dao_data", 'rb') as infile:
            prior_results = pickle.load(infile)
            results += prior_results
    with open("dao_data", 'wb') as out_file:
        pickle.dump(results, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

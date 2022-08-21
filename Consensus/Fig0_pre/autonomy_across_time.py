# -*- coding: utf-8 -*-
# @Time     : 8/5/2022 20:22
# @Author   : Junyi
# @FileName: Exp_s.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Superior import Superior
from Reality import Reality
# import matplotlib
# matplotlib.use('agg')  # For NUS HPC only
# import matplotlib.pyplot as plt
import pickle
import time
import multiprocessing as mp


def func(m=None, s=None, t=None, n=None, search_round=None,
         loop=None, return_dict=None):
    reality = Reality(m=m, s=s, t=t)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality,confirm=False)
    performance_across_time = []
    for _ in range(search_round):  # free search loop
        # diversity_across_time.append(superior.get_diversity())
        for individual in superior.individuals:
            individual.free_local_search()
        performance_list = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(performance_list) / len(performance_list))
    return_dict[loop] = performance_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 120  # Christina's paper: 100
    s = 3
    t = 2
    n = 500  # Christina's paper: 280
    search_round = 500
    repetition_round = 200  # Christina's paper
    version = "Rushed"
    authority = False  # Without authority
    diversity_across_para = []
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition_round):
        p = mp.Process(target=func, args=(m, s, t, n, search_round, loop, return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    performance_across_repetition = return_dict.values()  # Don't need dict index, since it is repetition.

    result_1 = []
    for i in range(search_round):
        temp = [payoff_list[i] for payoff_list in performance_across_repetition]
        result_1.append(sum(temp) / len(temp))
    # Save the original data for further analysis
    with open("Autonomy_performance_across_time", 'wb') as out_file:
        pickle.dump(result_1, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
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


def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version="Rushed", change_freq=None, change_prop=None, loop=None, return_dict=None):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    performance_across_time = []
    for loop in range(search_round):
        superior.local_search()
        performance_list = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(performance_list) / len(performance_list))
        if loop % change_freq == 0:
            reality.change(reality_change_rate=change_prop)
    return_dict[loop] = performance_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 60
    s = 1
    t = 2
    n = 200
    search_round = 500
    repetition_round = 400
    change_freq = 10
    change_prop = 0.1
    version = "Rushed"
    authority = 1.0  # Need the authority for Hierarchy!!
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition_round):
        p = mp.Process(target=func, args=(m, s, t, authority, n, search_round, version, change_freq, change_prop, loop, return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    diversity_across_repeat = return_dict.values()

    result_1 = []
    for i in range(search_round):
        temp = [payoff_list[i] for payoff_list in diversity_across_repeat]
        result_1.append(sum(temp) / len(temp))
    # Save the original data for further analysis
    with open("hierarchy_performance_under_turbulence", 'wb') as out_file:
        pickle.dump(result_1, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
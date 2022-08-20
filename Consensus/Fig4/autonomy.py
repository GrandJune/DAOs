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


def func(m=None, s=None, t=None, authority=None, n=None, search_round=None, version="Rushed", return_dict=None):
    reality = Reality(m=m, s=s, t=t)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    performance_across_time = []
    for _ in range(search_round):  # free search loop
        # diversity_across_time.append(superior.get_diversity())
        for individual in superior.individuals:
            individual.free_local_search(version=version)
        performance_list = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(performance_list) / len(performance_list))
    return_dict = performance_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 60
    s = 1
    t = 2
    n = 200
    search_round = 500
    repetition_round = 100
    turbulence_freq = 10
    change_proportion_list = [0.1, 0.2, 0.4, 0.6]
    version = "Rushed"
    authority = False
    diversity_across_para = []
    for chang_proportion in change_proportion_list:
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for i in range(repetition_round):
            p = mp.Process(target=func, args=(m, s, t, authority, n, search_round, version, return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        diversity_across_repeat = return_dict.values()

        result_1 = []
        for i in range(search_round):
            temp = [payoff_list[i] for payoff_list in diversity_across_repeat]
            result_1.append(sum(temp) / len(temp))
        diversity_across_para.append(result_1)
    # Save the original data for further analysis
    with open("Autonomy_performance", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
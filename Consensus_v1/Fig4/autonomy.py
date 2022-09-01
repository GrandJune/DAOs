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
from multiprocessing import Pool


def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version="Rushed", change_freq=None, change_prop=None):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    performance_across_time = []
    for loop in range(search_round):  # free search loop
        # diversity_across_time.append(superior.get_diversity())
        for individual in superior.individuals:
            individual.free_local_search()
        performance_list = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(performance_list) / len(performance_list))
        if loop % change_freq == 0:
            reality.change(reality_change_rate=change_prop)
    return performance_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    s = 3
    t = 3
    n = 500
    search_round = 600
    repetition_round = 300
    change_freq = 50
    change_prop = 0.2
    version = "Rushed"
    authority = False  # Without authority
    data_across_para = []
    cpu_num = mp.cpu_count()
    pool = Pool(cpu_num)
    data_across_repetition = []
    for i in range(repetition_round):
        data_across_repetition.append(
            pool.apply_async(func=func, args=((m, s, t, authority, n, search_round, version, change_freq, change_prop))).get())
    result_1 = []
    for i in range(search_round):
        temp = [data_list[i] for data_list in data_across_repetition]
        result_1.append(sum(temp) / len(temp))
    data_across_para.append(result_1)
    # Save the original data for further analysis
    with open("Autonomy_performance_under_turbulence", 'wb') as out_file:
        pickle.dump(result_1, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
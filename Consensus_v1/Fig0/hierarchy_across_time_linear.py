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


t0 = time.time()
m = 120  # Christina's paper: 100
s = 3
t = 1
n = 500  # Christina's paper: 280
search_round = 600
repetition_round = 500  # Christina's paper
version = "Rushed"
authority = 1.0  # Need the authority for Hierarchy!!

performance_across_repetition = []
for _ in range(repetition_round):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    performance_across_time = []
    for _ in range(search_round):
        superior.local_search()
        performance_list = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(performance_list) / len(performance_list))
    performance_across_repetition.append(performance_across_time)
result_1 = []
for i in range(search_round):
    temp = [payoff_list[i] for payoff_list in performance_across_repetition]
    result_1.append(sum(temp) / len(temp))

# Save the original data for further analysis
with open("hierarchy_performance_across_time", 'wb') as out_file:
    pickle.dump(result_1, out_file)
t1 = time.time()
print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
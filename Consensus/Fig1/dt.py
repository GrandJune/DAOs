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
import numpy as np


t0 = time.time()
m = 100  # Christina's paper: 100
s = 3
t_list = [1, 2, 3, 4, 5, 6, 7, 9, 10]
n = 100  # Christina's paper: 280
search_round = 200
repetition_round = 100  # Christina's paper
d_across_para = []
version = "Rushed"
for t in t_list:  # parameter
    if m % (s * t) != 0:
        m = s * t * (m // s // t)  # deal with the cell number issue
    manager_payoff_across_repeat = []
    for _ in range(repetition_round):  # repetation
        reality = Reality(m=m, s=s, t=t)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality, confirm=False)
        consensus = [0] * (m // s)
        for _ in range(search_round):  # free search loop
            for individual in superior.individuals:
                next_index = np.random.choice(len(consensus))
                next_policy = consensus[next_index]
                individual.constrained_local_search(focal_policy=next_policy, focal_policy_index=next_index)
            # form the consensus
            consensus = []
            for i in range(m//s):
                temp = sum(individual.policy[i] for individual in superior.individuals)
                if temp < 0:
                    consensus.append(-1)
                elif temp > 0:
                    consensus.append(1)
                else:
                    consensus.append(0)
        manager_performance = [individual.payoff for individual in superior.individuals]
        manager_payoff_across_repeat.append(sum(manager_performance) / len(manager_performance))
    d_across_para.append(sum(manager_payoff_across_repeat) / len(manager_payoff_across_repeat))


# Save the original data for further analysis
with open("DAO_performance_t", 'wb') as out_file:
    pickle.dump(d_across_para, out_file)
t1 = time.time()
print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

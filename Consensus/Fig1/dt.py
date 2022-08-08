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


m = 120  # Christina's paper: 100
s = 3
t_list = [1, 2, 3, 4, 5, 6, 7]
n = 280  # Christina's paper: 280
search_round = 200
repetition_round = 200  # Christina's paper
d_across_para = []
version = "Rushed"
t0 = time.time()
for t in t_list:  # parameter
    if m % (s * t) != 0:
        m = s * t * (m // s // t)  # deal with the cell number issue
    manager_payoff_across_repeat = []
    for _ in range(repetition_round):  # repetation
        reality = Reality(m=m, s=s, t=t)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
        manager_payoff_across_time = []
        for _ in range(search_round):  # free search loop
            for individual in superior.individuals:
                individual.free_local_search(version=version)
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
            for individual in superior.individuals:
                individual.confirm_to_supervision(policy=consensus)
            manager_performance = [individual.payoff for individual in superior.individuals]
            manager_payoff_across_time.append(sum(manager_performance) / len(manager_performance))
        manager_payoff_across_repeat.append(manager_payoff_across_time)

    result_1 = []
    for index in range(search_round):
        temp = [payoff_list[index] for payoff_list in manager_payoff_across_repeat]
        result_1.append(sum(temp) / len(temp))
    d_across_para.append(result_1)


# Save the original data for further analysis
with open("DAO_performance_t", 'wb') as out_file:
    pickle.dump(d_across_para, out_file)
t1 = time.time()
print("Time 1:", t1-t0)
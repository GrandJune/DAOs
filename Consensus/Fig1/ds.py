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
s_list = [1, 3, 5, 7, 9, 11]
t = 2
n = 500  # Christina's paper: 280
search_round = 500
repetition_round = 500  # Christina's paper
d_across_para = []
h_across_para = []
version = "Rushed"
for s in s_list:  # parameter
    if m % (s * t) != 0:
        m = s * t * (m // s // t)  # deal with the cell number issue
    manager_payoff_across_repeat = []
    for _ in range(repetition_round):  # repetation
        reality = Reality(m=m, s=s, t=t)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
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
        manager_payoff_across_repeat.append(sum(manager_performance) / len(manager_performance))
    d_across_para.append(sum(manager_payoff_across_repeat) / len(manager_payoff_across_repeat))

# Save the original data for further analysis
with open("DAO_performance_s", 'wb') as out_file:
    pickle.dump(d_across_para, out_file)

# x = range(search_round)
# plt.plot(x, overall_across_para[0], "k-", label="s=1")
# plt.plot(x, overall_across_para[1], "k--", label="s=3")
# # plt.plot(x, overall_across_para[2], "k:", label="s=5")
# plt.title('Overall Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("DAO_s_overall_performance.jpg")
# plt.clf()
#
# t1 = time.time()
# print("Time 3:", t1-t0)
# # Only managers
# x = range(search_round)
# plt.plot(x, manager_across_para[0], "k-", label="s=1")
# plt.plot(x, manager_across_para[1], "k--", label="s=3")
# # plt.plot(x, manager_across_para[2], "k:", label="s=5")
# plt.title('Manager Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("DAO_s_manager_performance.jpg")
# plt.clf()
# t1 = time.time()
# print("Time 3:", t1-t0)
# # Only superior
# x = range(search_round)
# plt.plot(x, superior_across_para[0], "k-", label="s=1")
# plt.plot(x, superior_across_para[1], "k--", label="s=3")
# # plt.plot(x, superior_across_para[2], "k:", label="s=5")
# plt.title('Superior Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("DAO_s_superior_performance.jpg")
# plt.clf()
# plt.close()
# t1 = time.time()
# print("Time 4:", t1-t0)
# plt.show()
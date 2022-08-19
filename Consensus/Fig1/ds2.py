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
m = 60  # Christina's paper: 100
s_list = [1, 3, 5]
t = 2
n = 100  # Christina's paper: 280
search_round = 600
repetition_round = 50  # Christina's paper
data_across_para = []
version = "Rushed"
for s in s_list:  # parameter
    m = 60
    if m % (s * t) != 0:
        m = s * t * (m // s // t)  # deal with the cell number issue
    performance_across_repeat = []
    for _ in range(repetition_round):  # repetation
        reality = Reality(m=m, s=s, t=t)
        consensus = [0] * (m // s)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=False)
        performance_across_time = []
        for _ in range(search_round):
            for individual in superior.individuals:
                next_index = np.random.choice(len(consensus))
                next_policy = consensus[next_index]
                individual.constrained_local_search_under_consensus(focal_policy=next_policy, focal_policy_index=next_index)
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
            performance_across_time.append(sum(manager_performance) / len(manager_performance))
        performance_across_repeat.append(performance_across_time)
    result = []
    for i in range(search_round):
        temp = [payoff_list[i] for payoff_list in performance_across_repeat]
        result.append(sum(temp) / len(temp))
    data_across_para.append(result)

# Save the original data for further analysis
with open("DAO_performance_s_2", 'wb') as out_file:
    pickle.dump(data_across_para, out_file)
t1 = time.time()
print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


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
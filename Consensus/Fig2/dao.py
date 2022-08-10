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
m = 120  # Christina's paper: 100
s = 3
t = 2
n = 500  # Christina's paper: 280
search_round = 500
repetition_round = 500  # Christina's paper

version = "Rushed"
diversity_across_repeat = []
for _ in range(repetition_round):  # repetation
    reality = Reality(m=m, s=s, t=t)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
    diversity_across_time = []
    consensus = [0] * m
    for _ in range(search_round):  # free search loop
        diversity_across_time.append(superior.get_diversity())
        for individual in superior.individuals:
            next_index = np.random.choice(range(m))
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
    diversity_across_repeat.append(diversity_across_time)

result_1 = []
for index in range(search_round):
    temp = [diversity_list[index] for diversity_list in diversity_across_repeat]
    result_1.append(sum(temp) / len(temp))

# Save the original data for further analysis
with open("DAO_diversity", 'wb') as out_file:
    pickle.dump(result_1, out_file)
t1 = time.time()
print(t1 - t0)


# x = range(search_round)
# plt.plot(x, result_1[0], "k-", label="DAO")
# # plt.plot(x, overall_across_para[2], "k:", label="s=5")
# plt.title('Diversity Decrease')
# plt.xlabel('Time')
# plt.ylabel('Diversity')
# plt.legend()
# plt.savefig("DAO_diversity.jpg")

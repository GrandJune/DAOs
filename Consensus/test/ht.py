# -*- coding: utf-8 -*-
# @Time     : 9/3/2022 14:51
# @Author   : Junyi
# @FileName: dao_s.py
# @Software  : PyCharm
# Observing PEP 8 coding style
# Comparison between Overall Payoff, Policy Payoff, and Belief Payoff
from Superior import Superior
from Reality import Reality
from Individual import Individual
import matplotlib.pyplot as plt
import numpy as np
import time

m = 24
s = 3
t_list = [1, 2, 4]
n = 100
data_across_para = []
version = "Weighted"
repetition_round = 100
search_round = 200
t0 = time.time()
for t in t_list:
    data_across_repetition = []
    for _ in range(repetition_round):
        reality = Reality(m=m, s=s, t=t, version=version)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=1.0)
        data_across_time = []
        for _ in range(search_round):
            superior.weighted_local_search()
            payoff_list = [individual.payoff for individual in superior.individuals]
            data_across_time.append(sum(payoff_list) / len(payoff_list))
        data_across_repetition.append(data_across_time)
    result_1 = []
    for i in range(search_round):
        temp = [payoff_list[i] for payoff_list in data_across_repetition]
        result_1.append(sum(temp) / len(temp))
    data_across_para.append(result_1)

x = range(search_round)
plt.plot(x, data_across_para[0], "k-", label="t=1")
plt.plot(x, data_across_para[1], "k--", label="t=2")
plt.plot(x, data_across_para[2], "k:", label="t=4")
# plt.savefig("search.jpg")
plt.title('Hierarchy Performance Across Strategic Complexity')
plt.xlabel('Iteration')
plt.ylabel('Performance')
plt.legend()
plt.savefig("Hierarchy_across_t.png")
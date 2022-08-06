# -*- coding: utf-8 -*-
# @Time     : 8/5/2022 16:57
# @Author   : Junyi
# @FileName: Exp_NonConsensus.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Superior import Superior
from Reality import Reality
from Individual import Individual
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import time
import pickle

# Comparison between Overall Payoff, Policy Payoff, and Belief Payoff
m = 120
s = 3
t_list = [1, 2, 4]
n = 200
search_round = 100
repetition_round = 500
alpha = 0.5
overall_across_para = []
manager_across_para = []
superior_across_para = []
version = "Rushed"
t0 = time.time()
for t in t_list: # parameter
    overall_payoff_across_repeat = []
    manager_payoff_across_repeat = []
    superior_payoff_across_repeat = []
    for _ in range(repetition_round):  # repetation
        reality = Reality(m=m, s=s, t=t, alpha=alpha)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
        superior.policy = []  # remove the policy
        overall_payoff_across_time = []
        manager_payoff_across_time = []
        superior_payoff_across_time = []
        for _ in range(search_round):  # free search loop
            for individual in superior.individuals:
                individual.free_local_search(version=version)

            overall_performance = [alpha * individual.payoff + (1-alpha) * superior.payoff for individual in superior.individuals]
            manager_performance = [individual.payoff for individual in superior.individuals]
            policy_performance = [individual.policy_payoff for individual in superior.individuals]
            overall_payoff_across_time.append(sum(overall_performance) / len(overall_performance))
            manager_payoff_across_time.append(sum(manager_performance) / len(manager_performance))
            superior_payoff_across_time.append(sum(policy_performance) / len(policy_performance))
        overall_payoff_across_repeat.append(overall_payoff_across_time)
        manager_payoff_across_repeat.append(manager_payoff_across_time)
        superior_payoff_across_repeat.append(superior_payoff_across_time)
    result_0 = []
    for index in range(search_round):
        temp = [payoff_list[index] for payoff_list in overall_payoff_across_repeat]
        result_0.append(sum(temp) / len(temp))
    overall_across_para.append(result_0)
    result_1 = []
    for index in range(search_round):
        temp = [payoff_list[index] for payoff_list in manager_payoff_across_repeat]
        result_1.append(sum(temp) / len(temp))
    manager_across_para.append(result_1)
    result_2 = []
    for index in range(search_round):
        temp = [payoff_list[index] for payoff_list in superior_payoff_across_repeat]
        result_2.append(sum(temp) / len(temp))
    superior_across_para.append(result_2)


x = range(search_round)
plt.plot(x, overall_across_para[0], "k-", label="t=1")
plt.plot(x, overall_across_para[1], "k--", label="t=2")
plt.plot(x, overall_across_para[2], "k:", label="t=4")
plt.title('Overall Performance')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
plt.savefig("Exp_NonConsensus_overall_performance.jpg")


# Only managers
x = range(search_round)
plt.plot(x, manager_across_para[0], "k-", label="t=1")
plt.plot(x, manager_across_para[1], "k--", label="t=2")
plt.plot(x, manager_across_para[2], "k:", label="t=4")
plt.title('Manager Performance')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
plt.savefig("Exp_NonConsensus_manager_performance.jpg")


# Only superior
x = range(search_round)
plt.plot(x, superior_across_para[0], "k-", label="t=1")
plt.plot(x, superior_across_para[1], "k--", label="t=2")
plt.plot(x, superior_across_para[2], "k:", label="t=4")
plt.title('Superior Performance')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
plt.savefig("Exp_NonConsensus_superior_performance.jpg")
t1 = time.time()
# print("Time spent: ", t1-t0)
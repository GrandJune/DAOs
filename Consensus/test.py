# -*- coding: utf-8 -*-
# @Time     : 6/11/2022 21:13
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Superior import Superior
from Reality import Reality
from Individual import Individual
import matplotlib.pyplot as plt
import numpy as np

# Bottom-up Consensus Structure
# m = 27
# s = 3
# t = 3
# n = 100
# alpha = 0.5
# reality = Reality(m=m, s=s, t=t, alpha=alpha)
# superior = Superior(m=m, s=s, t=t, n=n, reality=reality, alpha=alpha)
# superior.policy = []  # remove the policy
# payoff_list = []
# for _ in range(100):
#     for individual in superior.individuals:
#         if len(superior.policy) == 0:
#             individual.free_local_search()
#         else:
#             for index, value in enumerate(superior.policy):
#                 individual.constrained_local_search(focal_policy=value, focal_policy_index=index)
#         superior.beliefs.append(individual.belief)
#     superior.policy = []
#     for index in range(int(m/s)):
#         for individual in superior.individuals:
#             individual.individual_policy = []  # reset the policy dummy
#             for i in range(m // s):
#                 temp = sum(individual.belief[index] for index in range(i * s, (i + 1) *s))
#                 if temp < 0:
#                     individual.individual_policy.append(-1)
#                 else:
#                     individual.individual_policy.append(1)
#         temp = sum([individual.individual_policy[index] for individual in superior.individuals])
#         if temp > 0:
#             superior.policy.append(1)
#         elif temp == 0:
#             superior.policy.append(0)
#         else:
#             superior.policy.append(-1)
#     payoff_list.append(superior.payoff)
#
# x = range(100)
# plt.plot(x, payoff_list, "k-")
# # plt.savefig("search.jpg")
# plt.title('Performance Evolution')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.show()

# # Top-down hierarchy
# m = 24
# s = 3
# t = 1
# n = 100
# alpha = 0.5
#
# payoff_list_final = []
# for _ in range(1000):
#     reality = Reality(m=m, s=s, t=t, alpha=alpha)
#     superior = Superior(m=m, s=s, t=t, n=n, reality=reality, alpha=alpha)
#     payoff_list = []
#     for _ in range(50):
#         superior.local_search()
#         performance = [individual.payoff for individual in superior.individuals]
#         payoff_list.append(sum(performance) / len(performance))
#     payoff_list_final.append(payoff_list)
# result = []
# for index in range(50):
#     temp = [payoff_list[index] for payoff_list in payoff_list_final]
#     temp = sum(temp) / len(temp)
#     result.append(temp)
#
# x = range(50)
# plt.plot(x, result, "k-")
# # plt.savefig("search.jpg")
# plt.title('Performance Evolution')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.show()



# Bottom-up Consensus Structure (rushed payoff function)
# In this version, individual payoff is not associated with the policy dependency
# m = 24
# s = 3
# t_list = [1, 2, 4]
# n = 100
# alpha = 0.5
# results_across_t = []
# for t in t_list:
#     payoff_list_final = []
#     for _ in range(100):
#         reality = Reality(m=m, s=s, t=t, alpha=alpha)
#         superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
#         superior.policy = []  # remove the policy
#         payoff_list = []
#         for _ in range(100):
#             for individual in superior.individuals:
#                 individual.free_local_search()
#             performance = [individual.payoff for individual in superior.individuals]
#             payoff_list.append(sum(performance) / len(performance))
#         payoff_list_final.append(payoff_list)
#
#         for index in range(int(m/s)):
#             for individual in superior.individuals:
#                 individual.individual_policy = []  # reset the policy dummy
#                 for i in range(m // s):
#                     temp = sum(individual.belief[index] for index in range(i * s, (i + 1) *s))
#                     if temp < 0:
#                         individual.individual_policy.append(-1)
#                     else:
#                         individual.individual_policy.append(1)
#             temp = sum([individual.individual_policy[index] for individual in superior.individuals])
#             if temp > 0:
#                 superior.policy.append(1)
#             elif temp == 0:
#                 superior.policy.append(0)
#             else:
#                 superior.policy.append(-1)
#         for _ in range(20):
#             for index, value in enumerate(superior.policy):
#                 for individual in superior.individuals:
#                     individual.constrained_local_search(focal_policy=value, focal_policy_index=index)
#             performance = [individual.payoff for individual in superior.individuals]
#             payoff_list.append(sum(performance) / len(performance))
#         payoff_list_final.append(payoff_list)
#     result = []
#     for index in range(120):
#         temp = [payoff_list[index] for payoff_list in payoff_list_final]
#         result.append(sum(temp) / len(temp))
#     results_across_t.append(result)
#
# x = range(120)
# plt.plot(x, results_across_t[0], "k-", label="t=1")
# plt.plot(x, results_across_t[1], "k--", label="t=2")
# plt.plot(x, results_across_t[2], "k:", label="t=4")
# # plt.savefig("search.jpg")
# plt.title('DAO Performance Evolution')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.show()



# Top-down hierarchy
m = 24
s = 3
t_list = [1, 2, 4]
n = 100
alpha = 0.5

results_across_t = []
for t in t_list:
    payoff_list_final = []
    for _ in range(100):
        reality = Reality(m=m, s=s, t=t, alpha=alpha)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
        payoff_list = []
        for _ in range(100):
            superior.local_search()
            performance = [individual.payoff for individual in superior.individuals]
            payoff_list.append(sum(performance) / len(performance))
        payoff_list_final.append(payoff_list)
    result = []
    for index in range(100):
        temp = [payoff_list[index] for payoff_list in payoff_list_final]
        temp = sum(temp) / len(temp)
        result.append(temp)
    results_across_t.append(result)

x = range(100)
plt.plot(x, results_across_t[0], "k-", label="t=1")
plt.plot(x, results_across_t[1], "k--", label="t=2")
plt.plot(x, results_across_t[2], "k:", label="t=4")
# plt.savefig("search.jpg")
plt.title('Hierarchy Performance Evolution')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
plt.show()

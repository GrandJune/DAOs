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
import multiprocessing as mp
import pickle
# DAOs
# t0 = time.time()
# m = 24
# s_list = [1, 3, 5]
# t = 1
# n = 100
# data_across_para = []
# version = "Weighted"
# repetition_round = 100
# search_round = 200
# for s in s_list:
#     data_across_repetition = []
#     for _ in range(repetition_round):
#         reality = Reality(m=m, s=s, t=t, version=version)
#         superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=1.0)
#         data_across_time = []
#         consensus = [0] * (m // s)
#         for _ in range(search_round):
#             for individual in superior.individuals:
#                 next_index = np.random.choice(len(consensus))
#                 next_policy = consensus[next_index]
#                 individual.constrained_local_search_under_consensus(focal_policy=next_policy, focal_policy_index=next_index)
#             consensus = []
#             for i in range(m//s):
#                 temp = sum(individual.policy[i] * individual.payoff for individual in superior.individuals)
#                 if temp < 0:
#                     consensus.append(-1)
#                 elif temp > 0:
#                     consensus.append(1)
#                 else:
#                     consensus.append(0)
#             payoff_list = [individual.payoff for individual in superior.individuals]
#             data_across_time.append(sum(payoff_list) / len(payoff_list))
#         data_across_repetition.append(data_across_time)
#     result_1 = []
#     for i in range(search_round):
#         temp = [payoff_list[i] for payoff_list in data_across_repetition]
#         result_1.append(sum(temp) / len(temp))
#     data_across_para.append(result_1)
#
# x = range(search_round)
# plt.plot(x, data_across_para[0], "k-", label="t=1")
# plt.plot(x, data_across_para[1], "k--", label="t=2")
# plt.plot(x, data_across_para[2], "k:", label="t=4")
# # plt.savefig("search.jpg")
# plt.title('DAO Performance Across Strategic Complexity')
# plt.xlabel('Iteration')
# plt.ylabel('Performance')
# plt.legend()
# plt.show()
# plt.savefig("DAO_across_t.png")
#
# t1 = time.time()
# print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


# Huge multiprocessing
def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version=None, loop=None, return_dict=None):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=1.0)
    data_across_time = []
    consensus = [0] * (m // s)
    for _ in range(search_round):
        for individual in superior.individuals:
            next_index = np.random.choice(len(consensus))
            next_policy = consensus[next_index]
            individual.constrained_local_search_under_consensus(focal_policy=next_policy, focal_policy_index=next_index)
        consensus = []
        payoff_list = [individual.payoff for individual in superior.individuals]
        payoff_sum = sum(payoff_list)
        data_across_time.append(payoff_sum / n)
        for individual in superior.individuals:
            individual.token = individual.payoff / payoff_sum
        for i in range(m // s):
            temp = sum(individual.policy[i] * individual.token for individual in superior.individuals)
            if temp < -0.5:
                consensus.append(-1)
            elif temp > 0.5:
                consensus.append(1)
            else:
                consensus.append(0)

    return_dict[loop] = data_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 30
    s_list = [3, 5]
    t = 1
    n = 100
    data_across_para = []
    version = "Weighted"
    repetition_round = 100
    search_round = 200
    authority = False  # Without authority
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for s in s_list:
        for loop in range(repetition_round):
            p = mp.Process(target=func, args=(m, s, t, authority, n, search_round, version, loop, return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        data_across_repetition = return_dict.values()
        result_1 = []
        for i in range(search_round):
            temp = [payoff_list[i] for payoff_list in data_across_repetition]
            result_1.append(sum(temp) / len(temp))
        data_across_para.append(result_1)

    with open("dao_performance_across_time", 'wb') as out_file:
        pickle.dump(data_across_para, out_file)

    x = range(search_round)
    plt.plot(x, data_across_para[1], "b-", label="s=3")
    plt.plot(x, data_across_para[2], "g-", label="s=5")
    plt.title('DAO Performance Across Strategic Complexity')
    plt.xlabel('Iteration')
    plt.ylabel('Performance')
    plt.legend()
    plt.show()
    plt.savefig("DAO_across_t.png")
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
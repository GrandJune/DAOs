# -*- coding: utf-8 -*-
# @Time     : 8/5/2022 20:22
# @Author   : Junyi
# @FileName: Exp_s.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import time
from Superior import Superior
from Reality import Reality
# import matplotlib
# matplotlib.use('agg')
# import matplotlib.pyplot as plt
import pickle


t0 = time.time()
m = 60
s = 3
t_list = [1, 2, 4]
n = 280
search_round = 200
repetition_round = 200
alpha = 0.5
overall_across_para = []
manager_across_para = []
superior_across_para = []
version = "Rushed"
for t in t_list:  # parameter
    overall_payoff_across_repeat = []
    manager_payoff_across_repeat = []
    superior_payoff_across_repeat = []
    for _ in range(repetition_round):  # repetation
        reality = Reality(m=m, s=s, t=t, alpha=alpha)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
        overall_payoff_across_time = []
        manager_payoff_across_time = []
        superior_payoff_across_time = []
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

            overall_performance = [alpha * individual.payoff + (1-alpha) * individual.policy_payoff for individual in superior.individuals]
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

# Save the original data for further analysis
with open("DAO_overall_performance_t124", 'wb') as out_file:
    pickle.dump(overall_across_para, out_file)
with open("DAO_manager_performance_t124", 'wb') as out_file:
    pickle.dump(manager_across_para, out_file)
with open("DAO_superior_performance_t124", 'wb') as out_file:
    pickle.dump(superior_across_para, out_file)

t1 = time.time()
print("Time spent: ", t1-t0)

# x = range(search_round)
# plt.plot(x, overall_across_para[0], "k-", label="t=1")
# plt.plot(x, overall_across_para[1], "k--", label="t=2")
# plt.plot(x, overall_across_para[2], "k:", label="t=4")
# plt.title('Overall Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("DAO_t_overall_performance.jpg")
# plt.clf()
#
#
# # Only managers
# x = range(search_round)
# plt.plot(x, manager_across_para[0], "k-", label="t=1")
# plt.plot(x, manager_across_para[1], "k--", label="t=2")
# plt.plot(x, manager_across_para[2], "k:", label="t=4")
# plt.title('Manager Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("DAO_t_manager_performance.jpg")
# plt.clf()
#
#
# # Only superior
# x = range(search_round)
# plt.plot(x, superior_across_para[0], "k-", label="t=1")
# plt.plot(x, superior_across_para[1], "k--", label="t=2")
# plt.plot(x, superior_across_para[2], "k:", label="t=4")
# plt.title('Superior Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("DAO_t_superior_performance.jpg")
# plt.clf()
# plt.close()
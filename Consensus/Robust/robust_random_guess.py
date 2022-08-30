# -*- coding: utf-8 -*-
# @Time     : 8/5/2022 20:22
# @Author   : Junyi
# @FileName: Exp_s.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Superior import Superior
from Reality import Reality
# import matplotlib
# matplotlib.use('agg')
# import matplotlib.pyplot as plt
import pickle
import time


t0 = time.time()
m = 90  # Christina's paper: 100
s = 3
t = 6
n = 200  # Christina's paper: 280
search_round = 600
repetition_round = 300  # Christina's paper
authority = 1.0
version = "Rushed"
# Tough Search
performance_across_repeat_tough = []
for _ in range(repetition_round):  # repetation
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    performance_across_time = []
    for _ in range(search_round):  # free search loop
        superior.local_search()
        manager_performance = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(manager_performance) / len(manager_performance))
    performance_across_repeat_tough.append(performance_across_time)
result_1 = []
for index in range(search_round):
    temp = [payoff_list[index] for payoff_list in performance_across_repeat_tough]
    result_1.append(sum(temp) / len(temp))

# Random Guess
performance_across_repeat_random = []
for _ in range(repetition_round):  # repetation
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=True)
    performance_across_time = []
    for _ in range(search_round):  # free search loop
        superior.random_guess()
        manager_performance = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(manager_performance) / len(manager_performance))
    performance_across_repeat_random.append(performance_across_time)
result_2 = []
for index in range(search_round):
    temp = [payoff_list[index] for payoff_list in performance_across_repeat_random]
    result_2.append(sum(temp) / len(temp))

data_across_para = [result_1, result_2]
# Save the original data for further analysis
with open("robust_performance_random_guess", 'wb') as out_file:
    pickle.dump(data_across_para, out_file)
t1 = time.time()
print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

# x = range(search_round)
# plt.plot(x, h_across_para[0], "k-", label="s=1")
# plt.plot(x, overall_across_para[1], "k--", label="s=3")
# plt.plot(x, overall_across_para[2], "k:", label="s=5")
# plt.title('Overall Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.show()
# plt.savefig("Hierarchy_s_overall_performance.jpg")
# plt.clf()
#
# # Only managers
# x = range(search_round)
# plt.plot(x, manager_across_para[0], "k-", label="s=1")
# plt.plot(x, manager_across_para[1], "k--", label="s=3")
# plt.plot(x, manager_across_para[2], "k:", label="s=5")
# plt.title('Manager Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("Hierarchy_s_manager_performance.jpg")
# plt.clf()
#
# # Only superior
# x = range(search_round)
# plt.plot(x, superior_across_para[0], "k-", label="s=1")
# plt.plot(x, superior_across_para[1], "k--", label="s=3")
# plt.plot(x, superior_across_para[2], "k:", label="s=5")
# plt.title('Superior Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("Hierarchy_s_superior_performance.jpg")
# plt.clf()
#
# x = range(search_round)
# plt.plot(x, pure_superior_across_para[0], "k-", label="s=1")
# plt.plot(x, pure_superior_across_para[1], "k--", label="s=3")
# plt.plot(x, pure_superior_across_para[2], "k:", label="s=5")
# plt.title('Pure Superior Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("Hierarchy_s_pure_superior_performance.jpg")
# plt.clf()
# plt.close()
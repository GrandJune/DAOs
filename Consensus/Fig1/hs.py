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
m = 100  # Christina's paper: 100
s_list = [1, 3, 5, 7, 9, 11]
t = 2
n = 100  # Christina's paper: 280
search_round = 200
repetition_round = 100  # Christina's paper
d_across_para = []
h_across_para = []

for s in s_list:  # parameter
    if m % (s * t) != 0:
        m = s * t * (m // s // t)  # deal with the cell number issue
    manager_payoff_across_repeat = []
    for _ in range(repetition_round):  # repetation
        reality = Reality(m=m, s=s, t=t)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality, confirm=True)
        manager_payoff_across_time = []
        for _ in range(search_round):  # free search loop
            superior.local_search()
            manager_performance = [individual.payoff for individual in superior.individuals]
            manager_payoff_across_time.append(sum(manager_performance) / len(manager_performance))
        manager_payoff_across_repeat.append(manager_payoff_across_time)
    result_1 = []
    for index in range(search_round):
        temp = [payoff_list[index] for payoff_list in manager_payoff_across_repeat]
        result_1.append(sum(temp) / len(temp))
    h_across_para.append(result_1)

# Save the original data for further analysis
with open("Hierarchy_performance_s", 'wb') as out_file:
    pickle.dump(h_across_para, out_file)
t1 = time.time()
print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

# x = range(search_round)
# plt.plot(x, overall_across_para[0], "k-", label="s=1")
# plt.plot(x, overall_across_para[1], "k--", label="s=3")
# plt.plot(x, overall_across_para[2], "k:", label="s=5")
# plt.title('Overall Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
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
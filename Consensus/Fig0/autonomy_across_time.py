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


t0 = time.time()
m = 120  # Christina's paper: 100
s = 3
t = 2
n = 500  # Christina's paper: 280
search_round = 1000
repetition_round = 200  # Christina's paper
d_across_para = []
h_across_para = []
version = "Rushed"

manager_payoff_across_repeat = []
for _ in range(repetition_round):  # repetation
    reality = Reality(m=m, s=s, t=t)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, confirm=False)
    manager_payoff_across_time = []
    for _ in range(search_round):  # free search loop
        for individual in superior.individuals:
            individual.free_local_search(version=version)
        manager_performance = [individual.payoff for individual in superior.individuals]
        manager_payoff_across_time.append(sum(manager_performance) / len(manager_performance))
    manager_payoff_across_repeat.append(manager_payoff_across_time)

for i in range(search_round):
    temp = [payoff_list[i] for payoff_list in manager_payoff_across_repeat]
    d_across_para.append(sum(temp) / len(temp))

# Save the original data for further analysis
with open("Autonomy_performance_across_time", 'wb') as out_file:
    pickle.dump(d_across_para, out_file)
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
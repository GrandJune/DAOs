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
m = 60
s = 1
t = 2
n = 500
search_round = 300
repetition_round = 100
version = "Rushed"
authority = 0.8
diversity_across_repeat = []
for _ in range(repetition_round):  # repetition
    reality = Reality(m=m, s=s, t=t)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    diversity_across_time = []
    for _ in range(search_round):  # free search loop
        diversity_across_time.append(superior.get_diversity())
        superior.local_search()
    diversity_across_repeat.append(diversity_across_time)
    for individual in superior.individuals:
        if superior.get_distance(a=individual.belief, b=superior.policy) != 0:
            print(individual.belief)

result_1 = []
for index in range(search_round):
    temp = [diversity_list[index] for diversity_list in diversity_across_repeat]
    result_1.append(sum(temp) / len(temp))

# Save the original data for further analysis
with open("Hierarchy_diversity", 'wb') as out_file:
    pickle.dump(result_1, out_file)

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
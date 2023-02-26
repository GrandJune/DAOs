# -*- coding: utf-8 -*-
# @Time     : 10/3/2022 22:31
# @Author   : Junyi
# @FileName: Evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle
from matplotlib import container

data_folder = r"E:\data\dao-1023\DHA_2"
dao_performance_file = data_folder + r"\dao_performance_across_time"
hierarchy_performance_file = data_folder + r"\hierarchy_performance_across_time"
autonomy_performance_file = data_folder + r"\autonomy_performance_across_time"

consensus_performance_file = data_folder + r"\dao_consensus_performance_across_time"
superior_performance_file = data_folder + r"\hierarchy_superior_performance_across_time"

dao_diversity_file = data_folder + r"\dao_diversity_across_time"
hierarchy_diversity_file = data_folder + r"\hierarchy_diversity_across_time"
autonomy_diversity_file = data_folder + r"\autonomy_diversity_across_time"

with open(dao_performance_file, 'rb') as infile:
    dao_performance = pickle.load(infile)
with open(hierarchy_performance_file, 'rb') as infile:
    hierarchy_performance = pickle.load(infile)
with open(autonomy_performance_file, 'rb') as infile:
    autonomy_performance = pickle.load(infile)

with open(dao_diversity_file, 'rb') as infile:
    dao_diversity = pickle.load(infile)
with open(hierarchy_diversity_file, 'rb') as infile:
    hierarchy_diversity = pickle.load(infile)
with open(autonomy_diversity_file, 'rb') as infile:
    autonomy_diversity = pickle.load(infile)

with open(consensus_performance_file, 'rb') as infile:
    consensus_performance = pickle.load(infile)
with open(superior_performance_file, 'rb') as infile:
    superior_performance = pickle.load(infile)


# Plot performance across time (cannot use error bar, it has too many points)
x = range(len(dao_performance))
plt.plot(range(len(dao_performance)), dao_performance, "r-", label="DAO")
plt.plot(range(len(dao_performance)), consensus_performance, "r--", label="Consensus")
plt.plot(range(len(hierarchy_performance)), hierarchy_performance, "b-", label="Hierarchy")
plt.plot(range(len(hierarchy_performance)), superior_performance, "b--", label="Superior")
plt.plot(range(len(autonomy_performance)), autonomy_performance, "k-", label="Autonomy")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
# plt.xticks(x)
plt.legend(frameon=False, ncol=1, fontsize=10)
plt.savefig(data_folder + r"\DHA_performance.png", transparent=False, dpi=200)
plt.show()
plt.clf()


x = range(len(dao_performance))
plt.plot(range(len(dao_performance)), dao_diversity, "r-", label="DAO")
plt.plot(range(len(hierarchy_diversity)), hierarchy_diversity, "b-", label="Hierarchy")
plt.plot(range(len(autonomy_diversity)), autonomy_diversity, "k-", label="Autonomy")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
# plt.xticks(x)
plt.legend(frameon=False, ncol=1, fontsize=10)
plt.savefig(data_folder + r"\DHA_diversity.png", transparent=False, dpi=200)
plt.show()

# Performance
# x = range(len(dao_performance))
# fig, (ax1) = plt.subplots(1, 1)
# ax1.errorbar(x, dao_performance, yerr=dao_deviation, color="g", fmt="-", capsize=5, capthick=0.8, ecolor="g", label="DAO")
# ax1.errorbar(x, hierarchy_performance, yerr=hierarchy_deviation, color="b", fmt="-", capsize=5, capthick=0.8, ecolor="b", label="Hierarchy")
# # ax1.errorbar(x, autonomy_performance, yerr=autonomy_deviation, color="r", fmt="-", capsize=5, capthick=0.8, ecolor="r", label="Autonomy")
# plt.xlabel('Time', fontweight='bold', fontsize=10)
# plt.ylabel('Performance', fontweight='bold', fontsize=10)
# # plt.xticks(x)
# handles, labels = ax1.get_legend_handles_labels()
# handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
# plt.legend(handles, labels, numpoints=1, frameon=False)
# plt.savefig(data_folder + r"\DHA_performance.png", transparent=True, dpi=200)
# plt.show()


# two sample t-test
# from scipy import stats
# t_result = stats.ttest_ind(g_performance, t_performance, equal_var=False)
# print(t_result)
# print("END")
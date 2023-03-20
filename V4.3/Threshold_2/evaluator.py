# -*- coding: utf-8 -*-
# @Time     : 10/14/2022 17:06
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
from matplotlib import container
import pickle
import numpy as np


data_folder = r"E:\data\dao-0127\DAO_2\Threshold"
dao_performance_file = data_folder + r"\dao_performance_across_threshold"
dao_consensus_file = data_folder + r"\dao_consensus_performance_across_threshold"
dao_diversity_file = data_folder + r"\dao_diversity_across_threshold"
dao_variance_file = data_folder + r"\dao_variance_across_threshold"
with open(dao_performance_file, 'rb') as infile:
    dao_performance = pickle.load(infile)
with open(dao_variance_file, 'rb') as infile:
    dao_variance = pickle.load(infile)
with open(dao_diversity_file, 'rb') as infile:
    dao_diversity = pickle.load(infile)
with open(dao_consensus_file, 'rb') as infile:
    dao_consensus = pickle.load(infile)

dao_variance_2 = []
for variance_list in dao_variance:
    dao_variance_2.append(sum(variance_list) / len(variance_list))

x = np.arange(0.40, 0.71, 0.01)
fig, (ax1) = plt.subplots(1, 1)
ax1.plot(x, dao_consensus, "k--", label="Consensus")
ax1.errorbar(x, dao_performance, yerr=dao_variance_2, color="k", fmt="-", capsize=5, capthick=0.8, ecolor="g", label="DAO")
plt.xlabel('Threshold', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
# plt.xticks(x)
handles, labels = ax1.get_legend_handles_labels()
handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
plt.legend(handles, labels, loc='upper left', numpoints=1)
plt.savefig(data_folder + r"\Performance_across_threshold.png", transparent=False, dpi=200)
plt.clf()


# Diversity
fig, (ax1) = plt.subplots(1, 1)
plt.plot(x, dao_diversity, "k-", label="DAO")
# ax1.errorbar(x, dao_diversity, yerr=dao_deviation, color="k", fmt="-", capsize=5, capthick=0.8, ecolor="g", label="DAO")
plt.xlabel('Threshold', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
# plt.xticks(x)
handles, labels = ax1.get_legend_handles_labels()
handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
plt.legend(handles, labels, loc='upper left', numpoints=1)
plt.savefig(data_folder + r"\Diversity_across_threshold.png", transparent=False, dpi=200)
plt.clf()

# Deviation
fig, (ax1) = plt.subplots(1, 1)
ax1.plot(x, dao_variance_2, "k--", label="Deviation")
plt.xlabel('Threshold', fontweight='bold', fontsize=10)
plt.ylabel('Deviation', fontweight='bold', fontsize=10)
# plt.xticks(x)
plt.legend()
plt.savefig(data_folder + r"\Deviation_across_threshold.png", transparent=False, dpi=200)
plt.clf()
print("END")

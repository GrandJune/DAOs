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


data_folder = r"E:\data\dao-1018\Supervision"
performance_file = data_folder + r"\hierarchy_performance_across_threshold"
deviation_file = data_folder + r"\hierarchy_deviation_across_threshold"
diversity_file = data_folder + r"\hierarchy_diversity_across_threshold"
superior_file = data_folder + r"\superior_performance_across_threshold"

with open(performance_file, 'rb') as infile:
    performance = pickle.load(infile)
with open(deviation_file, 'rb') as infile:
    deviation = pickle.load(infile)
with open(diversity_file, 'rb') as infile:
    diversity = pickle.load(infile)
with open(superior_file, 'rb') as infile:
    superior = pickle.load(infile)

p1_list = np.arange(0.1, 1.0, 0.1)
fig, (ax1) = plt.subplots(1, 1)
ax1.errorbar(p1_list, performance, yerr=deviation, color="g", fmt="-", capsize=5, capthick=0.8, ecolor="g", label="Hierarchy")
plt.xlabel('P1', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.xticks(p1_list)
handles, labels = ax1.get_legend_handles_labels()
handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
plt.legend(handles, labels, loc='upper left', numpoints=1)
plt.savefig(data_folder + r"\Performance_across_p1.png", transparent=False, dpi=200)
# plt.show()
plt.clf()

fig, (ax1) = plt.subplots(1, 1)
ax1.plot(p1_list, diversity, "k-", label="Supervision")
plt.xlabel('P1', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.xticks(p1_list)
handles, labels = ax1.get_legend_handles_labels()
handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
plt.legend(handles, labels, loc='upper left', numpoints=1)
plt.savefig(data_folder + r"\Diversity_across_p1.png", transparent=False, dpi=200)
# plt.show()
plt.clf()


fig, (ax1) = plt.subplots(1, 1)
ax1.plot(p1_list, superior, "k-", label="Supervision")
plt.xlabel('P1', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.xticks(p1_list)
handles, labels = ax1.get_legend_handles_labels()
handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
plt.legend(handles, labels, loc='upper left', numpoints=1)
plt.savefig(data_folder + r"\Superior_performance_across_p1.png", transparent=False, dpi=200)
# plt.show()
plt.clf()
print("END")
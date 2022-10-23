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


data_folder = r"E:\data\dao-1023\Turbulence"
h_performance_file = data_folder + r"\hierarchy_performance"
d_performance_file = data_folder + r"\dao_performance"
a_performance_file = data_folder + r"\autonomy_performance"

h_diversity_file = data_folder + r"\hierarchy_diversity"
d_diversity_file = data_folder + r"\dao_diversity"
a_diversity_file = data_folder + r"\autonomy_diversity"

# superior_performance_file = data_folder + r"\hierarchy_superior_performance"
# consensus_performance_file = data_folder + r"\dao_consensus_performance"

with open(h_performance_file, 'rb') as infile:
    h_performance = pickle.load(infile)
with open(d_performance_file, 'rb') as infile:
    d_performance = pickle.load(infile)
with open(a_performance_file, 'rb') as infile:
    a_performance = pickle.load(infile)
with open(h_diversity_file, 'rb') as infile:
    h_diversity = pickle.load(infile)
with open(d_diversity_file, 'rb') as infile:
    d_diversity = pickle.load(infile)
with open(a_diversity_file, 'rb') as infile:
    a_diversity = pickle.load(infile)
# with open(superior_performance_file, 'rb') as infile:
#     superior_performance = pickle.load(infile)
# with open(consensus_performance_file, 'rb') as infile:
#     consensus_performance = pickle.load(infile)
#
# print(np.array(a_performance).shape)
h_performance_2 = []
for each in h_performance:
    h_performance_2.append(sum(each) / len(each))
d_performance_2 = []
for each in d_performance:
    d_performance_2.append(sum(each) / len(each))
h_diversity_2 = []
for each in h_diversity:
    h_diversity_2.append(sum(each) / len(each))
d_diversity_2 = []
for each in d_diversity:
    d_diversity_2.append(sum(each) / len(each))

x = range(len(h_performance))
plt.plot(x, h_performance_2, "k--", label="Hierarchy")
plt.plot(x, d_performance_2, "k-", label="DAO")
plt.plot(x, a_performance, "k:", label="Autonomy")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
# plt.xticks(x)
plt.legend()
plt.savefig(data_folder + r"\Performance_turbulence.png", transparent=False, dpi=200)
plt.clf()

fifig, (ax1) = plt.subplots(1, 1)
ax1.plot(x, h_diversity_2, "k--", label="Hierarchy")
ax1.plot(x, d_diversity_2, "k-", label="DAO")
ax1.plot(x, a_diversity, "k:", label="Autonomy")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
# plt.xticks(p1_list)
plt.legend()
plt.savefig(data_folder + r"\Diversity_turbulence.png", transparent=False, dpi=200)
plt.clf()
print("END")
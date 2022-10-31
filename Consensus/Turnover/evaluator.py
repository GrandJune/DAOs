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


data_folder = r"F:\data\dao-1023\Turnover_1"
d_performance_file = data_folder + r"\dao_performance"
d_consensus_file = data_folder + r"\dao_consensus_performance"
h_performance_file = data_folder + r"\hierarchy_performance"
h_superior_file = data_folder + r"\hierarchy_superior_performance"
a_performance_file = data_folder + r"\autonomy_performance"

d_diversity_file = data_folder + r"\dao_diversity"
h_diversity_file = data_folder + r"\hierarchy_diversity"
a_diversity_file = data_folder + r"\autonomy_diversity"
# diversity_file = data_folder + r"\hierarchy_diversity"
# superior_file = data_folder + r"\hierarchy_superior_performance"

with open(d_performance_file, 'rb') as infile:
    d_performance = pickle.load(infile)
with open(d_consensus_file, 'rb') as infile:
    d_consensus = pickle.load(infile)
with open(h_performance_file, 'rb') as infile:
    h_performance = pickle.load(infile)
with open(h_superior_file, 'rb') as infile:
    h_superior = pickle.load(infile)
with open(a_performance_file, 'rb') as infile:
    a_performance = pickle.load(infile)


with open(d_diversity_file, 'rb') as infile:
    d_diversity = pickle.load(infile)
with open(h_diversity_file, 'rb') as infile:
    h_diversity = pickle.load(infile)
with open(a_diversity_file, 'rb') as infile:
    a_diversity = pickle.load(infile)

d_performance_2 = []
for each in d_performance:
    d_performance_2.append(sum(each) / len(each))
h_performance_2 = []
for each in h_performance:
    h_performance_2.append(sum(each) / len(each))

d_diversity_2 = []
for each in d_diversity:
    d_diversity_2.append(sum(each) / len(each))
h_diversity_2 = []
for each in h_diversity:
    h_diversity_2.append(sum(each) / len(each))

d_x = range(len(d_performance))
h_x = range(len(h_performance))
a_x = range(len(a_performance))
plt.plot(d_x, d_performance_2, "k-", label="DAO")
plt.plot(h_x, h_performance_2, "k--", label="Hierarchy")
plt.plot(a_x, a_performance, "k:", label="Autonomy")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.legend()
plt.savefig(data_folder + r"\Performance_under_turnover.png", transparent=False, dpi=200)
# plt.show()
plt.clf()
plt.plot(d_x, d_diversity_2, "k-", label="DAO")
plt.plot(h_x, h_diversity_2, "k--", label="Hierarchy")
plt.plot(a_x, a_diversity, "k:", label="Autonomy")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
plt.legend()
plt.savefig(data_folder + r"\Diversity_under_turnover.png", transparent=False, dpi=200)
# plt.show()
plt.clf()

plt.plot(d_x, d_consensus, "r--", label="Consensus")
plt.plot(h_x, h_superior, "g--", label="Authority")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
plt.legend()
plt.savefig(data_folder + r"\Consensus_Superior_under_turnover.png", transparent=False, dpi=200)
print("END")

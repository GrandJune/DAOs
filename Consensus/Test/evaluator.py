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


data_folder = r"E:\data\dao-1023\Asymmetry_3"
performance_file = data_folder + r"\dao_performance"
diversity_file = data_folder + r"\dao_diversity"
consensus_file = data_folder + r"\dao_consensus_performance"

with open(performance_file, 'rb') as infile:
    performance = pickle.load(infile)
with open(diversity_file, 'rb') as infile:
    diversity = pickle.load(infile)
with open(consensus_file, 'rb') as infile:
    consensus = pickle.load(infile)

x = range(len(performance[0]))
# asymmetry_list = [1, 2, 4, 8]
plt.plot(x, performance[0], "r-", label="Symmetry")
plt.plot(x, performance[1], "y-", label="High Asymmetry")
plt.plot(x, performance[2], "g-", label="Medium Asymmetry")
plt.plot(x, performance[3], "b-", label="Low Asymmetry")
# plt.plot(x, performance[4], "k-", label="a=8")
# plt.title("a is negatively correlated with inequality")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.legend()
plt.savefig(data_folder + r"\Performance_across_asymmetry.png", transparent=False, dpi=200)
# plt.show()
plt.clf()


x = range(len(performance[0]))
# asymmetry_list = [1, 2, 4, 8]
plt.plot(x, diversity[0], "r-", label="Symmetry")
plt.plot(x, diversity[1], "y-", label="High Asymmetry")
plt.plot(x, diversity[2], "g-", label="Medium Asymmetry")
plt.plot(x, diversity[3], "b-", label="Low Asymmetry")
# plt.plot(x, diversity[4], "k-", label="a=8")
# plt.title("a is negatively correlated with inequality")
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
plt.legend()
plt.savefig(data_folder + r"\Diversity_across_asymmetry.png", transparent=False, dpi=200)
print("END")
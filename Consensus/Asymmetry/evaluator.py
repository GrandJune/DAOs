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


data_folder = r"E:\data\dao-1023\Asymmetry"
performance_file = data_folder + r"\dao_performance"
diversity_file = data_folder + r"\dao_diversity"
consensus_file = data_folder + r"\dao_consensus_performance"

with open(performance_file, 'rb') as infile:
    performance = pickle.load(infile)
with open(diversity_file, 'rb') as infile:
    diversity = pickle.load(infile)
with open(consensus_file, 'rb') as infile:
    consensus = pickle.load(infile)

performance_final = []
for data_para in performance:
    performance_para = []
    for data_search in data_para:
        temp = sum(data_search) / len(data_search)
        performance_para.append(temp)
    performance_final.append(performance_para)

# asymmetry_list = [1, 2, 4, 8]
plt.plot(range(1200), performance_final[0], "k-", label="a=1")
# plt.plot(range(1200), performance_final[1], "k--", label="a=2")
# plt.plot(range(1200), performance_final[2], "k:", label="a=4")
# plt.plot(range(1200), performance_final[3], "k.", label="a=8")
plt.xlabel('P1', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.legend()
plt.savefig(data_folder + r"\Performance_across_asymmetry.png", transparent=False, dpi=200)
# plt.show()
# plt.clf()

print("END")
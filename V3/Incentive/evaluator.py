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


data_folder = r"E:\data\dao-0127\Incentive"
performance_file = data_folder + r"\dao_performance"
consensus_file = data_folder + r"\dao_consensus_performance"
diversity_file = data_folder + r"\dao_diversity"
original_performance_file = data_folder + r"\dao_original_performance"
original_consensus_file = data_folder + r"\dao_original_consensus_performance"

with open(performance_file, 'rb') as infile:
    performance = pickle.load(infile)
with open(consensus_file, 'rb') as infile:
    consensus = pickle.load(infile)
with open(diversity_file, 'rb') as infile:
    diversity = pickle.load(infile)
with open(original_performance_file, 'rb') as infile:
    original_performance = pickle.load(infile)
with open(original_consensus_file, 'rb') as infile:
    original_consensus = pickle.load(infile)

promotion_list = [0, 1, 2, 4]
for index, each in enumerate(performance):
    plt.plot(range(len(each)), each, label="Promotion={0}".format(promotion_list[index]))
    # break
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
# plt.xticks(promotion_list)
plt.legend()
plt.savefig(data_folder + r"\Performance_across_promotion.png", transparent=False, dpi=200)
plt.show()
plt.clf()

for index, each in enumerate(diversity):
    plt.plot(range(len(each)), each, label="Promotion={0}".format(promotion_list[index]))
    # break
plt.xlabel('Time', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
# plt.xticks(promotion_list)
plt.legend()
plt.savefig(data_folder + r"\Diversity_across_promotion.png", transparent=False, dpi=200)
plt.show()
plt.clf()

print("END")
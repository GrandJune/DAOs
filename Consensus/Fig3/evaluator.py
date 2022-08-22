# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


folder = r"C:\Python_Workplace\dao-0820\Consensus\Fig3"
diversity_file = folder + r"\dao_diversity_across_asymmetry"
with open(diversity_file, 'rb') as in_file:
    diversity_data = pickle.load(in_file)
performance_file = folder + r"\dao_performance_across_asymmetry"
with open(performance_file, 'rb') as in_file:
    performance_data = pickle.load(in_file)

x = range(len(performance_data[0]))
plt.plot(x, performance_data[0], "r-", label="a=1")
plt.plot(x, performance_data[1], "b-", label="a=2")
plt.plot(x, performance_data[2], "g-", label="a=4")
plt.plot(x, performance_data[3], "y-", label="a=8")
# plt.title('Diversity Decrease')
plt.xlabel('Iteration', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.legend(frameon=False, ncol=2, fontsize=10)
plt.savefig("Performance_across_a.png", transparent=True, dpi=1200)
plt.savefig(folder + "\Performance_across_a.png", transparent=True, dpi=1200)
plt.show()
# plt.clf()
# plt.close()


x = range(len(diversity_data[0]))
plt.plot(x, diversity_data[0], "r-", label="a=1")
plt.plot(x, diversity_data[1], "b-", label="a=2")
plt.plot(x, diversity_data[2], "g-", label="a=4")
plt.plot(x, diversity_data[3], "y-", label="a=8")
# plt.title('Diversity Decrease')
plt.xlabel('Iteration', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
plt.legend(frameon=False, ncol=2, fontsize=10)
plt.savefig("Diversity_across_a.png", transparent=True, dpi=1200)
plt.savefig(folder + "\Diversity_across_a.png", transparent=True, dpi=1200)
plt.show()
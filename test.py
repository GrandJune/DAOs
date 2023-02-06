# -*- coding: utf-8 -*-
# @Time     : 1/31/2023 14:03
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import matplotlib.pyplot as plt

def gini(x):
    """Compute Gini coefficient of array of values"""
    diffsum = 0
    for i, xi in enumerate(x[:-1], 1):
        diffsum += np.sum(np.abs(xi - x[i:]))
    return diffsum / (len(x)**2 * np.mean(x))


asymmetry_list = [2]
mode = 1
xx = []
for asymmetry in asymmetry_list:
    x = []
    for _ in range(100):
        x.append((np.random.pareto(a=asymmetry) + 1) * mode)
    xx.append(x)

# the histogram of the data
color_list = ["r", "b", "y"]
count_list = []
bins_list = []
for x in xx:
    count, bins, _ = plt.hist(x, 1000, density=True)
    count_list.append(count)
    bins_list.append(bins)
    plt.clf()

for count, bins, asymmetry, color in zip(count_list, bins_list, asymmetry_list, color_list):
    fit = asymmetry * mode ** asymmetry / bins ** (asymmetry + 1)
    plt.plot(bins, max(count) * fit / max(fit), linewidth=2, color=color)
    # plt.xticks((0, 6))
plt.show()




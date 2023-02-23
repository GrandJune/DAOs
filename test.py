# -*- coding: utf-8 -*-
# @Time     : 1/31/2023 14:03
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import matplotlib.pyplot as plt

def gini(array):
    array = sorted(array)
    n = len(array)
    coefficient = 0
    for i, value in enumerate(array):
        coefficient += (2 * i - n) * value
    coefficient /= n * sum(array)
    return coefficient

asymmetry_list = [1, 2, 3]
mode = 1
xx = []
for asymmetry in asymmetry_list:
    x = []
    for _ in range(1000):
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
for x in xx:
    gini_index = gini(x)
    print("Gini Index: ", gini_index)

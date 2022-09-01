# -*- coding: utf-8 -*-
# @Time     : 8/19/2022 19:28
# @Author   : Junyi
# @FileName: pareto_test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import numpy as np

# Using numpy.random.pareto() method
token_list = np.random.pareto(8, 1000)
print(sum(token_list))
# print(gfg[:10]/sum(gfg))
# gfg = np.random.pareto(10, 1000)
# gfg = [i / sum(gfg) for i in gfg]
print(max(token_list)/min(token_list))
plt.plot(token_list)
plt.show()

def gini(x):
    # (Warning: This is a concise implementation, but it is O(n**2)
    # in time and memory, where n = len(x).  *Don't* pass in huge
    # samples!)

    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad/np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad
    return g

print(gini(token_list))

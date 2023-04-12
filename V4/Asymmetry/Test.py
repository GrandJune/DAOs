# -*- coding: utf-8 -*-
# @Time     : 2/15/2023 19:51
# @Author   : Junyi
# @FileName: Tet.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import quantecon as qe
import matplotlib.pyplot as plt
# from numba import njit, jitclass, float64, prange

# n = 10_000                      # size of sample
# w = np.exp(np.random.randn(n))  # lognormal draws
# f_vals, l_vals = qe.lorenz_curve(w)
# fig, ax = plt.subplots()
# ax.plot(f_vals, l_vals, label='Lorenz curve, lognormal sample')
# ax.plot(f_vals, f_vals, label='Lorenz curve, equality')
# ax.legend()
# plt.show()
# plt.clf()


def gini(array):
    array = sorted(array)
    n = len(array)
    coefficient = 0
    for i, value in enumerate(array):
        coefficient += (2 * i + 1) * value
    coefficient /= n * sum(array)
    coefficient -= (n + 1) / n
    return coefficient


# a_vals = [1, 2, 3]
# ginis = []
# ginis_theoretical = []
# n = 1000
#
# fig, ax = plt.subplots()
# for a in a_vals:
#     y = np.random.pareto(a, size=n)
#     ginis.append(qe.gini_coefficient(y))
#     ginis_theoretical.append(gini(y))
# print(ginis)
# ax.plot(a_vals, ginis, label='estimated gini coefficient')
# ax.plot(a_vals, ginis_theoretical, label='theoretical gini coefficient')
# ax.legend()
# ax.set_xlabel("Pareto Distrubtion Parameter $\\rho$")
# ax.set_ylabel("Gini coefficient")
# plt.show()
# print("END")
# for _ in range(1000)
# y = np.random.pareto(a, size=n)
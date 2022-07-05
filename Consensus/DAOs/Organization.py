# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 16:17
# @Author   : Junyi
# @FileName: Organization.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality
from Individual import Individual
import math
import matplotlib.pyplot as plt
import time


class Organization:
    def __init__(self, n=None, beta=None, m=None, s=None,
                 reality=None, size=None, index=None):
        self.n = n
        self.m = m
        self.s = s
        self.index = index
        self.reality = reality
        self.code = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3]).tolist()
        self.payoff = self.reality.get_payoff(belief=self.code)
        self.size = size  # initial size (will be self-organized over time)
        # DV
        self.performance = 0

    def get_majority_view(self):
        for dimension in range(self.m):
            dimension_dominant = 0
            for member in self.individuals:
                dimension_dominant += member.belief[dimension]
            if dimension_dominant > 0:
                self.code.append(1)
            elif dimension_dominant < 0:
                self.code.append(-1)
            else:
                self.code.append(0)

    def get_distance(self, belief_1=None, belief_2=None):
        res = 0
        for i in range(self.m):
            if belief_1[i] == belief_2[i]:
                res += 1
        return res / self.m

    def describe(self):
        print("-" * 10)
        print("n: {0}, size: {1}, m: {2}, s: {3}".format(self.n, self.size, self.m, self.s))
        print("Real Belief: ", self.reality.real_code)
        print("-" * 10)


if __name__ == '__main__':
    t0 = time.time()
    n = 280
    beta = 0
    m = 10
    s = 2
    lr = 0.3
    subgroup_size = 7
    reality_change_rate = 0
    change_freq = None
    loop = 100





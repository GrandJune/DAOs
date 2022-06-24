# -*- coding: utf-8 -*-
# @Time     : 6/23/2022 20:57
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np


class Reality:
    def __init__(self, m=None):
        self.m = m
        self.code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5]).tolist()

    def get_payoff(self, belief=None):
        res = 0
        for i in range(self.m):
            if self.code[i] == belief[i]:
                res += 1
            # elif self.code[i] + belief[i] == 0:  # totally wrong element
            #     res -= 1
        return res / self.m

    def turbulence(self):
        self.code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5]).tolist()


if __name__ == '__main__':
    m = 30
    reality = Reality(m=m)
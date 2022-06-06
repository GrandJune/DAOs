# -*- coding: utf-8 -*-
# @Time     : 6/6/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import math

class Reality:
    def __init__(self, m=10, s=0):
        self.m = m
        self.s = s
        if self.s == 0:
            raise ValueError("s cannot be zero")
        if self.s > self.m:
            raise ValueError("s ({0}) is greater than m ({1})".format(self.s, self.m))
        self.cluster_num = math.ceil(m / s)
        self.real_code = np.random.choice([0,1], self.m, p=[0.5, 0.5])
        # self.payoff = 0

    def describe(self):
        print("m: {0}, s: {1}, cluster: {2}".format(self.m, self.s, self.cluster_num))
        print("Reality Code: ", self.real_code)
        # print("Payoff: ", self.payoff)
        print("*"*10)

    def get_payoff(self, solution=None):
        ress = 0
        for i in range(self.cluster_num):
            result = 1
            for j in range(self.s):
                index = j + i * self.s
                if index < self.m:
                    if self.real_code[index] == solution[index]:
                        result = 1
                    else:
                        result = 0
                        break
                else:
                    break
            ress += result
        ress *= self.s
        return ress


if __name__ == '__main__':
    reality = Reality(m=40, s=3)
    # reality.describe()
    result = reality.get_payoff(solution=[1]*10)
    reality.describe()
    print(result)
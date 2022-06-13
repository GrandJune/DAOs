# -*- coding: utf-8 -*-
# @Time     : 6/6/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import math

class Reality:
    def __init__(self, m=10, s=0, reality_change=None):
        self.m = m
        self.s = s
        if self.s == 0:
            raise ValueError("s cannot be zero")
        if self.s > self.m:
            raise ValueError("s ({0}) is greater than m ({1})".format(self.s, self.m))
        self.cluster_num = math.ceil(m / s)
        self.real_code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])

    def describe(self):
        print("m: {0}, s: {1}, cluster: {2}".format(self.m, self.s, self.cluster_num))
        print("Reality Code: ", self.real_code)
        # print("Payoff: ", self.payoff)
        print("*"*10)

    def get_payoff_discrete(self, belief=None):
        """
        The main calculation cost -- Need to design it carefully
        :param belief:
        :return:
        """
        ress = 0
        for i in range(self.cluster_num):
            result = 1
            for j in range(self.s):
                index = j + i * self.s
                if index < self.m:
                    if self.real_code[index] != belief[index]:
                        result = 0
                        break
                else:
                    break
            ress += result
        ress *= self.s
        return ress

    def get_payoff_bidirection(self, belief=None):
        """
        The main calculation cost -- Need to design it carefully
        :param belief:
        :return:get the payoff of the specific belief
        """
        ress = 0
        for i in range(self.cluster_num):
            correct_num = 0
            for j in range(self.s):
                index = i * self.s + j
                if self.real_code[index] * belief[index] == 1:
                    correct_num += 1
            ress += np.random.choice([0, correct_num], p=[1-correct_num / self.s, correct_num / self.s])
        return ress

    def change(self, reality_change_rate=None):
        if reality_change_rate:
            for index in range(self.m):
                if np.random.uniform(0, 1) < reality_change_rate:
                    self.real_code[index] *= -1


if __name__ == '__main__':
    m = 10
    s = 3
    reality = Reality(m=m, s=s)
    # reality.describe()
    result = reality.get_payoff(belief=[1]*m)
    reality.describe()
    print(result)
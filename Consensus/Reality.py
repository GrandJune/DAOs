# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import time
import numpy as np
import math
from itertools import product


class Reality:
    def __init__(self, m=None, s=None, version="Rushed"):
        self.m = m
        self.s = s
        if self.s < 1:
            raise ValueError("The number of complexity should be greater than 0")
        if self.s > self.m:
            raise ValueError("The number of complexity should be less than the number of reality")
        self.version = version
        self.cell_num = math.ceil(m / s)
        self.real_code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.real_policy = self.belief_2_policy(belief=self.real_code)

    def get_payoff(self, belief=None):
        ress = 0
        if self.version == "Rushed":
            for i in range(self.cell_num):
                if np.array_equiv(belief[i*self.s: (i+1)*self.s], self.real_code[i*self.s: (i+1)*self.s]):
                    ress += 1
            ress = ress * self.s / self.m
        elif self.version == "Penalty":
            for i in range(self.cell_num):
                temp = 0
                for j in range(self.s):
                    temp += belief[i*self.s + j] * self.real_code[i*self.s + j]
                ress += temp
            ress /= self.m
        return ress

    def get_policy_payoff(self, policy=None, mode="Normal"):
        if mode == "Penalty":
            temp = [a*b for a, b in zip(self.real_policy, policy)]
            return sum(temp) / len(policy)
        elif mode == "Normal":
            res = 0
            for a, b in zip(self.real_policy, policy):
                if a == b:
                    res += 1
            return res / len(policy)

    def belief_2_policy(self, belief=None):
        policy = []
        for i in range(self.cell_num):
            temp = sum(belief[i * self.s:(i + 1) * self.s])
            if temp < 0:
                policy.append(-1)
            elif temp > 0:
                policy.append(1)
            else:
                policy.append(0)
        return policy

    def policy_2_belief(self, policy=None):
        temp = list(product([1, -1], repeat=self.s))
        if policy == 1:
            temp = [each for each in temp if sum(each) > 0]
        elif policy == -1:
            temp = [each for each in temp if sum(each) < 0]
        else:pass
        return temp[np.random.choice(len(temp))]


if __name__ == '__main__':
    m = 20
    s = 5
    version = "Rushed"
    reality = Reality(m=m, s=s, version=version)
    # belief = reality.real_code.copy()
    # belief[-1] *= -1
    # payoff = reality.get_payoff(belief=belief)
    # print(payoff)
    # print(reality.cell_num)
    belief = reality.policy_2_belief(policy=1)
    print(belief)


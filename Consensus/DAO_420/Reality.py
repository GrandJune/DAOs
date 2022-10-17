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
        if m % 3 != 0:
            raise ValueError("m is not dividable by 3")
        if m % s != 0:
            raise ValueError("m is not dividable by s")
        if self.s < 1:
            raise ValueError("The number of complexity should be greater than 0")
        if self.s > self.m:
            raise ValueError("The number of complexity should be less than the number of reality")
        self.version = version
        self.policy_num = self.m // 3
        self.real_code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.real_policy = self.belief_2_policy(belief=self.real_code)

    def get_payoff(self, belief=None):
        ress = 0
        if self.version == "Rushed":
            for i in range(self.m // self.s):
                if np.array_equiv(belief[i * self.s: (i + 1) * self.s], self.real_code[i * self.s: (i + 1) * self.s]):
                    ress += 1
            ress = ress * self.s / self.m
        elif self.version == "Penalty":
            for i in range(self.policy_num):
                temp = 0
                for j in range(self.s):
                    temp += belief[i * self.s + j] * self.real_code[i * self.s + j]
                ress += temp
            ress /= self.m
        return ress

    def get_policy_payoff(self, policy=None, mode="Normal"):
        if mode == "Penalty":
            temp = [a * b for a, b in zip(self.real_policy, policy)]
            return sum(temp) / len(policy)
        elif mode == "Normal":
            res = 0
            for a, b in zip(self.real_policy, policy):
                if a == b:
                    res += 1
            return res / len(policy)

    def belief_2_policy(self, belief=None):
        policy = []
        for i in range(self.policy_num):
            temp = sum(belief[i * 3: (i + 1) * 3])
            if temp < 0:
                policy.append(-1)
            elif temp > 0:
                policy.append(1)
            else:
                policy.append(0)
        return policy

    def policy_2_belief(self, policy=None):
        temp = list(product([1, -1], repeat=3))
        if policy == 1:
            temp = [each for each in temp if sum(each) > 0]
        elif policy == -1:
            temp = [each for each in temp if sum(each) < 0]
        else:
            pass
        return temp[np.random.choice(len(temp))]

    def get_majority_view(self, superior_belief=None):
        majority_view = []
        for i in range(self.m):
            temp = [belief[i] for belief in superior_belief]
            if sum(temp) > 0:
                majority_view.append(1)
            elif sum(temp) < 0:
                majority_view.append(-1)
            else:
                majority_view.append(0)
        return majority_view


if __name__ == '__main__':
    m = 12
    s = 1
    version = "Rushed"
    reality = Reality(m=m, s=s, version=version)
    # belief = reality.real_code.copy()
    # belief[-1] *= -1
    # payoff = reality.get_payoff(belief=belief)
    # print(payoff)
    # print(reality.cell_num)
    belief = reality.policy_2_belief(policy=1)
    print(belief)
    # print("real_code: ", reality.real_code)
    # test_belief = np.random.choice((1, -1), m, p=[0.5, 0.5])
    # print("test_belief: ", test_belief)
    # print(reality.get_payoff(belief=test_belief))
    # test_policy = reality.belief_2_policy(belief=test_belief)
    # print("test_policy: ", test_policy)



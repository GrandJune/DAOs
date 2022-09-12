# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import time
import numpy as np
import math


class Reality:
    def __init__(self, m=None, s=None, t=None, version="Rushed", sigma=None):
        self.m = m  # the total length of the reality code
        self.s = s  # the lower-level of interdependency (staff interdependency)
        self.t = t  # the upper-level of interdependency (policy interdependency)
        self.sigma = sigma  # adjust weights of payoff across strategic cells (asymmetric payoff)
        if self.m % (self.s * self.t) != 0:
            raise ValueError("m must be a multiple of (s * t)")
        if self.s < 1:
            raise ValueError("The number of complexity should be greater than 0")
        if self.s > self.m:
            raise ValueError("The number of complexity should be less than the number of reality")
        self.weight_list = self.get_payoff_weights()
        self.version = version
        self.cell_num_1 = math.ceil(m / s)
        self.cell_num_2 = math.ceil(self.cell_num_1 / t)
        self.real_code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.real_policy = self.belief_2_policy(belief=self.real_code)

    def describe(self):
        print("m: {0}, s: {1}, code_cell/policy: {2}, policy_cell".format(self.m, self.s, self.cell_num_1, self.cell_num_2))
        print("Reality Code: ", self.real_code)
        print("*"*10)

    def get_payoff(self, belief=None):
        if len(belief) == self.m:
            reference = self.real_code
            cell_num = math.ceil(self.m / self.s)
            complexity = self.s
        else:
            reference = self.real_policy
            cell_num = math.ceil(self.m / self.s / self.t)
            complexity = self.t
        ress = 0  # normalized payoff: the highest payoff is one
        if self.version == "Rushed":
            for i in range(cell_num):
                if np.array_equiv(belief[i*complexity: (i+1)*complexity], reference[i*complexity: (i+1)*complexity]):
                    ress += 1
            ress *= (complexity / len(belief))
        elif self.version == "Penalty":
            for i in range(len(belief)):
                ress += belief[i] * reference[i]
            ress *= (complexity / len(belief))  # equal weight of s / m, or t/(m //s)
        elif self.version == "Weighted":
            if len(belief) == self.m:  # Belief
                for i in range(cell_num):
                    if np.array_equiv(belief[i*complexity: (i+1)*complexity], reference[i*complexity: (i+1)*complexity]):
                        ress += self.weight_list[i]
            else:  # Policy
                for i in range(cell_num):
                    if np.array_equiv(belief[i * complexity: (i + 1) * complexity],
                                      reference[i * complexity: (i + 1) * complexity]):
                        ress += sum(self.weight_list[i * complexity: (i + 1) * complexity])
        elif self.version == "DualWeighted":
            if len(belief) == self.m:  # Belief
                for i in range(cell_num):
                    if np.array_equiv(belief[i*complexity: (i+1)*complexity], reference[i*complexity: (i+1)*complexity]):
                        ress += self.weight_list[i]
            else:  # Policy
                for i in range(cell_num):
                    if np.array_equiv(belief[i * complexity: (i + 1) * complexity],
                                      reference[i * complexity: (i + 1) * complexity]):
                        ress += sum(self.weight_list[i * complexity: (i + 1) * complexity])

            for i in range(self.cell_num_2):
                correct_num = 0
                for j in range(self.t):
                    index = i * self.t + j
                    if index >= self.cell_num_1:
                        break
                    else:
                        if self.real_policy[index] * policy[index] == 1:
                            correct_num += 1
                if correct_num == 0:
                    continue
                else:
                    ress += np.random.choice([0, correct_num], p=[1-correct_num / self.cell_num_1, correct_num / self.cell_num_1])
        return ress

    def structural_change(self):
        self.weight_list = self.get_payoff_weights()

    def frictional_change(self, reality_change_rate=None):
        if reality_change_rate:
            for index in range(self.m):
                if np.random.uniform(0, 1) < reality_change_rate:
                    self.real_code[index] *= -1
            self.real_policy = self.belief_2_policy(belief=self.real_code)

    def belief_2_policy(self, belief):
        policy = []
        for i in range(self.cell_num_1):
            temp = sum(belief[i * self.s:(i + 1) * self.s])
            if temp < 0:
                policy.append(-1)
            elif temp > 0:
                policy.append(1)
            else:
                policy.append(0)
        return policy

    def get_payoff_weights(self):
        weight_list = []
        for i in range(math.ceil(self.m / self.s)):
            weight_list.append(np.random.normal(loc=0, scale=0.4))
        weight_list = [abs(each) for each in weight_list]
        weight_list = [each / sum(weight_list) for each in weight_list]
        return weight_list


if __name__ == '__main__':
    m = 20
    s = 2
    t = 1
    version = "Weighted"
    reality = Reality(m, s, t, version=version)
    # belief = [1] * 6
    belief = reality.real_code.copy()
    belief[-1] *= -1
    t0 = time.time()
    for _ in range(100):
        payoff = reality.get_payoff(belief=belief)
        print(reality.real_code)
        print(belief)
        print(payoff)
    t1 = time.time()
    # print(t1-t0)
    # print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


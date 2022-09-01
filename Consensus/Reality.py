# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
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

    def get_belief_payoff(self, belief=None):
        if self.version == "Smooth":
            ress = 0
            for i in range(self.cell_num_1):
                correct_num = 0
                for j in range(self.s):
                    index = i * self.s + j
                    if index >= self.m:
                        break
                    else:
                        if self.real_code[index] * belief[index] == 1:
                            correct_num += 1
                if correct_num == 0:
                    continue
                else:
                    ress += np.random.choice([0, correct_num], p=[1-correct_num / self.s, correct_num / self.s])
            return ress / self.m
        elif self.version == "Rushed":
            ress = 0
            for i in range(self.cell_num_1):
                flag = False
                for j in range(self.s):
                    index = i * self.s + j
                    # print(self.real_code, belief)
                    if self.real_code[index] == belief[index]:
                        flag = True
                    else:
                        flag = False
                        break
                if flag:
                    ress += self.s
            return ress / self.m
        elif self.version == "Penalty":
            ress = 0
            for i in range(self.cell_num_1):
                acc = 0
                for j in range(self.s):
                    index = i * self.s + j
                    # print(self.real_code, belief)
                    if self.real_code[index] == belief[index]:
                        acc += 1
                    elif self.real_code[index] * belief[index] == -1:
                        acc -= 1
                    else:  # belief[index] == 0
                        continue
                    ress += acc
            return ress / self.m

    def get_policy_payoff(self, policy=None):
        ress_upper = 0
        if self.version == "Rushed":
            for i in range(self.cell_num_2):
                flag = False
                for j in range(self.t):
                    index = i * self.t + j
                    if self.real_policy[index] != policy[index]:
                        flag = False
                        break
                    else:
                        flag = True
                if flag:
                    ress_upper += self.t
            return ress_upper / self.cell_num_1

        elif self.version == "Smooth":
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
                    ress_upper += np.random.choice([0, correct_num], p=[1-correct_num / self.cell_num_1, correct_num / self.cell_num_1])
            return ress_upper / self.cell_num_1
        elif self.version == "Penalty":
            for i in range(self.cell_num_2):
                correct_num = 0
                for j in range(self.t):
                    index = i * self.t + j
                    if index >= self.cell_num_1:
                        break
                    if self.real_policy[index] == policy[index]:
                        correct_num += 1
                    elif self.real_policy[index] * policy[index] == -1:
                        correct_num -= 1
                    else:  # policy[index] == 0
                        continue
                    ress_upper += correct_num
            return ress_upper / self.cell_num_1
        elif self.version == "Weighted":
            # assign different weights for domains or specialization
            for i in range(self.cell_num_2):
                flag = False
                for j in range(self.t):
                    index = i * self.t + j
                    if self.real_policy[index] != policy[index]:
                        flag = False
                        break
                    else:
                        flag = True
                if flag:
                    ress_upper += self.t * self.weight_list[i]

    def strategic_change(self, reality_change_rate=None):
        pass

    def operational_change(self, reality_change_rate=None):
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
        # follow labor division paper: # specialization vs generalization
        # using sigma to control the narrow specialization of payoff
        # But what is the intuition? what does it represent the real business world.
        # Can consensus identify the change in strategical structure change
        # In labor division, it represents the skill specialization
        # model this through a strategy prominence distribution for every strategic domain
        # in which strategic salience differ across all domains and sum up to one.
        weight_list = []
        for i in range(self.cell_num_1):
            weight_list.append(np.random.normal(loc=1, scale=1))



if __name__ == '__main__':
    m = 6
    s = 2
    t = 1
    version = "Rushed"
    reality = Reality(m, s, t, version=version)
    # belief = [1] * 6
    belief = reality.real_code.copy()
    belief[-1] *= -1
    payoff = reality.get_belief_payoff(belief=belief)
    print(reality.real_code)
    print(belief)
    print(payoff)
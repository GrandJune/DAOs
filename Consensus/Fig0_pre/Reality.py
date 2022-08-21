# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import math


class Reality:
    def __init__(self, m=None, s=None, t=None, alpha=0.5, version="Rushed"):
        self.m = m  # the total length of the reality code
        self.s = s  # the lower-level of interdependency (staff interdependency)
        self.t = t  # the upper-level of interdependency (policy interdependency)
        if self.m % (self.s * self.t) != 0:
            raise ValueError("m must be a multiple of (s * t)")
        if self.s % 2 == 0:
            raise ValueError("s must be an odd number")
        if self.s < 1:
            raise ValueError("The number of complexity should be greater than 0")
        if self.s > self.m:
            raise ValueError("The number of complexity should be less than the number of reality")
        if not alpha:
            raise ValueError("alpha is absent for Reality class")
        self.cell_num_1 = math.ceil(m / s)
        self.cell_num_2 = math.ceil(m / s / t)
        self.version = version
        self.real_code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.real_policy = self.belief_2_policy(belief=self.real_code)

    def describe(self):
        print("m: {0}, s: {1}, code_cell/policy: {2}, policy_cell".format(self.m, self.s, self.cell_num_1, self.cell_num_2))
        print("Reality Code: ", self.real_code)
        print("*"*10)

    def get_belief_payoff(self, belief=None, version="Rushed"):
        if version == "Smooth":
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
        elif version == "Rushed":
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

    def get_hierarchy_payoff_rushed(self, alpha=None, belief_list=None, belief=None, policy=None, version="Rushed"):
        """

        :param alpha: can borrowed from reality
        :param belief_list: if it's superior, there is a group of managers
        :param belief: if it's manager, there is only one belief
        :param policy: could be superior's or manager's belief
        :param version: "Rushed" or "Smooth"
        :return: integrated payoff
        """
        if alpha:
            self.alpha = alpha
        # lower-level payoff
        if len(belief):
            lower_payoff = self.get_belief_payoff(belief, version)
        elif len(belief_list):
            lower_payoff = [self.get_belief_payoff(belief, version) for belief in belief_list]
            lower_payoff = sum(lower_payoff) / len(lower_payoff)
        else:
            raise ValueError("Either belief or beliefs is needed!")
        # upper-level payoff
        upper_payoff = self.get_policy_payoff(policy=policy, version=version)
        return self.alpha * lower_payoff + (1 - self.alpha) * upper_payoff

    def get_policy_payoff(self, policy=None, version="Rushed"):
        ress_upper = 0
        if version == "Rushed":
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
        elif version == "Smooth":
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

    def change(self, reality_change_rate=None):
        if reality_change_rate:
            for index in range(self.m):
                if np.random.uniform(0, 1) < reality_change_rate:
                    self.real_code[index] *= -1
            self.real_policy = self.belief_2_policy(belief=self.real_code)

    def belief_2_policy(self, belief):
        policy = []
        for i in range(self.cell_num_1):
            temp = sum(belief[index] for index in range(i * self.s, (i + 1) * self.s))
            if temp < 0:
                policy.append(-1)
            elif temp > 0:
                policy.append(1)
            else:
                policy.append(0)
        return policy


if __name__ == '__main__':
    m = 18
    s = 3
    t = 3
    alpha = 0.5
    reality = Reality(m, s, t, alpha)

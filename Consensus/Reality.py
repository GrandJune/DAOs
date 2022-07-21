# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import math


class Reality:
    def __init__(self, m=None, s=None, t=None, alpha=None):
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
        self.cell_num_1 = math.ceil(m / s)
        self.cell_num_2 = math.ceil(m / s / t)
        self.alpha = alpha
        self.real_code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.real_policy = self.belief_2_policy(belief=self.real_code)

    def describe(self):
        print("m: {0}, s: {1}, code_cell/policy: {2}, policy_cell".format(self.m, self.s, self.cell_num_1, self.cell_num_2))
        print("Reality Code: ", self.real_code)
        print("*"*10)

    def get_smooth_payoff(self, belief=None):
        """
        Calculate the payoff of the belief (smooth version)
        # A generalized payoff function for Christina's m/s payoff function
        # when correct_num = 0, and s, the payoff expectation would be 0 and s, respectively.
        # That's the Christina's model.
        # for correct_num varying from 1 to (s-1), the expectation would be (correct_num)^2/s
        :param belief: either the individual belief or the organizational code
        :return: payoff
        """
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
            ress += np.random.choice([0, correct_num], p=[1-correct_num / self.s, correct_num / self.s])
        return ress / self.m

    def get_rushed_payoff(self, belief=None):
        """
        Calculate the payoff of the belief (rushed version)
        :param belief: either the individual belief or the organizational code
        :return: rushed payoff for belief (i.e., either s or 0)
        """
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

    def get_hierarchy_payoff_rushed(self, alpha=None, belief_list=None, belief=None, policy=None):
        """
        Calculate the hierarchical payoff, based on the rushed payoff function
        :param alpha: the weight of the lower-level payoff
        :return: the weighted payoff combination
        """
        if alpha:
            self.alpha = alpha
        # lower-level payoff
        if len(belief):
            lower_payoff = self.get_rushed_payoff(belief)
        elif len(belief_list):
            lower_payoff = [self.get_rushed_payoff(belief) for belief in belief_list]
            lower_payoff = sum(lower_payoff) / len(lower_payoff)
        else:
            raise ValueError("Either belief or beliefs is needed!")
        # upper-level payoff
        upper_payoff = self.get_policy_payoff(policy)
        return self.alpha * lower_payoff + (1 - self.alpha) * upper_payoff

    def get_policy_payoff(self, policy=None):
        ress_upper = 0
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

    def change(self, reality_change_rate=None):
        if reality_change_rate:
            for index in range(self.m):
                if np.random.uniform(0, 1) < reality_change_rate:
                    self.real_code[index] *= -1
            self.real_policy = self.belief_2_policy(belief=self.real_code)

    def generate_task(self, task_size=None):
        if not task_size:
            task_size = math.ceil(self.m * 0.5)
        task = np.random.choice(range(self.m), task_size, p=[1 / self.m] * self.m)
        return task

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

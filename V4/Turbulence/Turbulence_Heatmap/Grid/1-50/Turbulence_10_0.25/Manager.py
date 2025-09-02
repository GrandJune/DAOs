# -*- coding: utf-8 -*-
# @Time     : 10/23/2022 19:04
# @Author   : Junyi
# @FileName: Manager.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np


class Manager:
    def __init__(self, policy_num=None, reality=None, p1=None):
        self.policy_num = policy_num
        self.reality = reality
        self.p1 = p1
        self.policy = np.random.choice([-1, 0, 1], self.policy_num, p=[1/3, 1/3, 1/3])
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)

    def turnover(self, turnover_rate=None):
        for index in range(self.policy_num):
            if np.random.uniform(0, 1) < turnover_rate:
                self.policy = np.random.choice([-1, 0, 1], self.policy_num, p=[1 / 3, 1 / 3, 1 / 3])
                self.payoff = self.reality.get_policy_payoff(policy=self.policy)

    def experimentation(self, experimentation_rate=None):
        for index in range(self.policy_num):
            if np.random.uniform(0, 1) < experimentation_rate:
                self.policy[index] *= -1
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)

    def learn_from_code(self, code=None):
        next_policy = self.policy.copy()
        for index in range(self.policy_num):
            if code[index] == 0:
                continue
            if np.random.uniform(0, 1) < self.p1:
                next_policy[index] = code[index]
        self.policy = next_policy
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)

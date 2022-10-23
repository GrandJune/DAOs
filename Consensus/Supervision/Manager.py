# -*- coding: utf-8 -*-
# @Time     : 10/23/2022 19:04
# @Author   : Junyi
# @FileName: Manager.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np


class Manager:
    def __init__(self, m=None, reality=None, p1=None):
        self.m = m
        self.reality = reality
        self.p1 = p1
        self.policy = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)

    def turnover(self):
        self.policy = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)

    def learn_from_code(self, code=None):
        next_policy = self.policy.copy()
        for index in range(self.m):
            if code[index] == 0:
                continue
            if np.random.uniform(0, 1) < self.p1:
                next_policy[index] = code[index]
        self.policy = next_policy
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)

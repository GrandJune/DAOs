# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 19:53
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import time
import numpy as np
from Reality import Reality


class Individual:
    def __init__(self, m=None, s=None, reality=None, lr=None):
        self.m = m
        self.s = s
        self.lr = lr  # learning rate, learning from consensus
        self.token = None
        self.connections = []  # for autonomy, to seek for superior subgroup
        self.reality = reality
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.policy = self.reality.belief_2_policy(belief=self.belief)  # a fake policy for voting
        self.payoff = self.reality.get_payoff(belief=self.belief)

    def learning_from_policy(self, policy=None):
        for i in range(self.m // self.s):
            if np.random.uniform(0, 1) < self.lr:
                self.belief[i * self.s: (i + 1) * self.s] = self.reality.policy_2_belief(policy=policy[i])
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)


if __name__ == '__main__':
    m = 30
    s = 2
    t = 1
    n = 4
    lr = 0.3
    version = "Rushed"
    reality = Reality(m=m, s=s, version=version)
    individual = Individual(m=m, s=s, reality=reality, lr=0.3)
    # belief_test = reality.real_code.copy()
    # belief_test[-1] = -1 * belief_test[-1]
    # print(belief_test)
    # print(reality.real_code)
    # payoff_test = reality.get_payoff(belief_test)
    # print(payoff_test)
    consensus = np.random.choice((-1, 1), m // s, p=[0.5, 0.5])
    for _ in range(100):
        individual.learning_from_policy(consensus)
        print(individual.payoff)
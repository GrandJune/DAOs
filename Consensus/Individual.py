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
    def __init__(self, m=None, s=None, reality=None, lr=None, auto_lr=None):
        self.m = m
        self.s = s
        self.lr = lr  # learning rate, learning from consensus/policy
        self.auto_lr = auto_lr  # autonomous leaning
        self.token = None  # should introduce more dimensions of token
        self.connections = []  # for autonomy, to seek for superior subgroup
        self.reality = reality
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy_num = self.m // 3
        self.policy = self.reality.belief_2_policy(belief=self.belief)  # a fake policy for voting
        self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

    def learning_from_policy(self, policy=None):
        next_belief = self.belief.copy()
        for i in range(self.policy_num):
            if np.random.uniform(0, 1) < self.lr:
                next_belief[i * 3: (i + 1) * 3] = self.reality.policy_2_belief(policy=policy[i])
                next_payoff = self.reality.get_payoff(belief=next_belief)
                if next_payoff > self.payoff:
                    self.belief = next_belief.copy()  # update the belief
                else:
                    next_belief = self.belief.copy()  # temp goes back to the current belief
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

    def learning_from_belief(self, belief=None):
        if len(belief) != self.m:
            raise ValueError("Learning from a wrong belief (not autonomous majority view)")
        for i in range(self.m):
            if np.random.uniform(0, 1) < self.auto_lr:
                self.belief[i] = belief[i]
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)


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
    for _ in range(1000):
        individual.learning_from_policy(consensus)
        print(individual.payoff)
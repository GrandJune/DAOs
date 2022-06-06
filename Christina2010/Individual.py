# -*- coding: utf-8 -*-
# @Time     : 6/6/2022 19:53
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality


class Individual:
    def __init__(self, m=40, s=1, reality=None, learn=0.1):
        self.m = m
        self.s = s
        self.belief = np.random.choice([0, 1], self.m, p=[0.5, 0.5])
        self.learn = learn
        self.connections = []  # the list of agents connected to the focal agent
        # using the index of individuals list as the network index
        self.payoff = reality.get_payoff(solution=self.belief)
        self.reality = reality

    def describe(self):
        print("m: {0}, s: {1}".format(self.m, self.s))
        print("belief: ", self.belief)
        print("reality: ", self.reality.real_code)
        print("learning rate: ", self.learn)
        print("connection list: ", self.connections)
        print("payoff: ", self.payoff)

    def local_search(self):
        success = 0
        focal_index = np.random.choice(range(self.m), p=[1 / self.m] * self.m)
        next_belief = self.belief.copy()
        next_belief[focal_index] = 1 - next_belief[focal_index]
        # print(next_belief, self.belief)
        next_payoff = self.reality.get_payoff(solution=next_belief)
        # print(next_belief, self.belief, next_payoff, self.payoff)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            success = 1
        return success

    def learn(self, majority_view):
        if np.random.uniform(0, 1) < self.learn:
            self.belief = majority_view

    def turnover(self):
        """
        Recreate this individual
        :return:
        """
        self.belief = np.random.choice([0, 1], self.m, p=[0.5, 0.5])
        self.payoff = reality.get_payoff(solution=self.belief)


if __name__ == '__main__':
    m = 40
    s = 4
    reality = Reality(m=m, s=s)
    # reality.describe()
    individual = Individual(m=m, s=s, reality=reality)
    success = 0
    for _ in range(200):
        success += individual.local_search()
        # print(individual.belief, individual.payoff)
    print(reality.real_code)
    print("success: ", success)
    individual.describe()

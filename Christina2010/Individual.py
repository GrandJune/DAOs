# -*- coding: utf-8 -*-
# @Time     : 6/6/2022 19:53
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality


class Individual:
    def __init__(self, m=None, s=None, reality=None, lr=None, index=None):
        self.m = m
        self.s = s
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.lr = lr
        self.index = index
        self.cluster = None
        self.connections = []  # the list of agents connected to the focal agent
        # using the index of individuals list as the network index
        self.reality = reality
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.majority_view = []

    def describe(self):
        print("*" * 10)
        print("m: {0}, s: {1}".format(self.m, self.s))
        print("belief: ", self.belief)
        print("reality: ", self.reality.real_code)
        print("learning rate: ", self.lr)
        print("connection list: ", [index for index, value in enumerate(self.connections) if value == 1])
        print("payoff: ", self.payoff)
        print("*" * 10)

    def learn(self):
        if not self.majority_view:
            return
        for index in range(self.m):
            if self.majority_view[index] == 0:
                continue
            if np.random.uniform(0, 1) < self.lr:
                self.belief[index] = self.majority_view[index]
        self.payoff = self.reality.get_payoff(belief=self.belief)

    def turnover(self):
        """
        Recreate this individual
        :return:
        """
        self.belief = np.random.choice([0, 1], self.m, p=[0.5, 0.5])
        self.payoff = reality.get_payoff(belief=self.belief)


if __name__ == '__main__':
    m = 10
    s = 5
    lr = 0
    reality = Reality(m=m, s=s)
    # reality.describe()
    individual = Individual(m=m, s=s, reality=reality, lr=lr)
    individual.describe()

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
        self.freedom_space = []

    def describe(self):
        print("*" * 10)
        print("m: {0}, s: {1}".format(self.m, self.s))
        print("belief: ", self.belief)
        print("reality: ", self.reality.real_code)
        print("learning rate: ", self.lr)
        print("connection list: ", [index for index, value in enumerate(self.connections) if value == 1])
        print("payoff: ", self.payoff)
        print("*" * 10)

    def local_search_slim(self):
        success = 0
        self.freedom_space = [i for i in range(self.m) if self.belief[i] != 0]
        if len(self.freedom_space) == 0:
            return 0
        focal_index = np.random.choice(self.freedom_space, p=[1 / len(self.freedom_space)] * len(self.freedom_space))
        next_belief = self.belief.copy()
        next_belief[focal_index] = -1 * next_belief[focal_index]
        # print(next_belief, self.belief)G
        next_payoff = self.reality.get_payoff(belief=next_belief)
        # print(next_belief, self.belief, next_payoff, self.payoff)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            self.freedom_space.remove(focal_index)
            success = 1
        return success

    def local_search_hover(self):
        success = 0
        while True:
            focal_index = np.random.choice(range(self.m), p=[1 / self.m] * self.m)
            next_belief = self.belief.copy()
            if next_belief[focal_index] != 0:
                next_belief[focal_index] = -1 * next_belief[focal_index]
            else:
                continue
        next_payoff = self.reality.get_payoff(belief=next_belief)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            success = 1
        return success

    def learn(self):
        if not self.majority_view:
            return
        for index in range(self.m):
            if np.random.uniform(0, 1) < self.lr:
                self.belief[index] = self.majority_view[index]

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
    success = 0
    for _ in range(200):
        success += individual.local_search()
        print(individual.belief, individual.payoff)
    print(reality.real_code)
    print("success: ", success)
    individual.describe()

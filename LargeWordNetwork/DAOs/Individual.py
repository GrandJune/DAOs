# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 19:53
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality


class Individual:
    def __init__(self, m=None, s=None, reality=None,
                 lr=None, index=None, beta=None):
        self.m = m
        self.s = s
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.lr = lr
        self.beta = beta
        self.index = index
        self.cluster = None
        self.connections = []  # the list of agents connected to the focal agent
        self.belonging = 0
        self.reality = reality
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.freedom_space = [index for index, value in enumerate(self.belief) if value != 0]

    def describe(self):
        print("*" * 10)
        print("m: {0}, s: {1}".format(self.m, self.s))
        print("belief: ", self.belief)
        print("learning rate: ", self.lr)
        print("connection list: ", [index for index, value in enumerate(self.connections) if value == 1])
        print("payoff: ", self.payoff)
        print("*" * 10)

    def local_search(self):
        success = 0
        if len(self.freedom_space) == 0:
            return success
        focal_index = np.random.choice(self.freedom_space)
        next_belief = self.belief.copy()
        next_belief[focal_index] *= -1
        next_payoff = self.reality.get_payoff(belief=next_belief)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            self.freedom_space.remove(focal_index)
            success = 1
        return success

    def learn(self, code=None):
        for index in range(self.m):
            if np.random.uniform(0, 1) < self.lr:
                self.belief[index] = code[index]
                if index not in self.freedom_space:
                    self.freedom_space.append(index)


if __name__ == '__main__':
    m = 280
    s = 2
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

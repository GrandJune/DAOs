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
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3]).tolist()
        # self.next_belief = self.belief.copy()
        self.lr = lr
        self.beta = beta
        self.index = index
        self.belonging = 0
        self.reality = reality
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.freedom_space = [index for index, value in enumerate(self.belief) if value != 0]
        self.superior_belief = None  # learn from peers

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
        focal_index = np.random.choice(range(self.m))
        next_belief = self.belief.copy()
        next_belief[focal_index] *= -1  # zero will remain zero
        next_payoff = self.reality.get_payoff(belief=next_belief)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            success = 1
        return success

    def learn_from_code(self, code=None):
        # learn from the code
        for index in range(self.m):
            if np.random.uniform(0, 1) < self.lr:
                self.belief[index] = code[index]
                if index not in self.freedom_space:
                    self.freedom_space.append(index)

    def learn_from_peers(self):
        for index in range(self.m):
            if np.random.uniform(0, 1) < self.lr:
                self.belief[index] = self.superior_belief[index]
                if index not in self.freedom_space:
                    self.freedom_space.append(index)



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

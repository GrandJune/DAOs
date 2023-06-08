# -*- coding: utf-8 -*-
# @Time     : 6/23/2022 21:00
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality


class Individual:
    def __init__(self, index=None, m=None, p1=None, reality=None):
        self.index = index
        self.m = m
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        # self.action = self.belief.copy()
        # for index in range(self.m):
        #     if self.action[index] == 0:
        #         self.action[index] = np.random.choice([-1, 1])
        self.p1 = p1  # socialization rate
        self.reality = reality
        self.payoff = self.reality.get_payoff(belief=self.belief)

    def learn_from_code(self, code=None):
        next_belief = self.belief.copy()
        for index in range(self.m):
            if code[index] == 0:
                continue
            if np.random.uniform(0, 1) < self.p1:
                next_belief[index] = code[index]
        self.belief = next_belief
        # self.action = self.belief.copy()
        # for index in range(self.m):
        #     if self.action[index] == 0:
        #         self.action[index] = np.random.choice([-1, 1])
        self.payoff = self.reality.get_payoff(belief=self.belief)

    def get_similarity(self, belief_1=None, belief_2=None):
        res = 0
        for i in range(self.m):
            if belief_1 == belief_2:
                res += 1
        return res

    def get_dominant_belif(self, belief_list=None):
        res = [0] * self.m
        for index in range(self.m):
            temp = sum([each[index] for each in belief_list])
            if temp > 0:
                res[index] = 1
            elif temp < 0:
                res[index] = -1
        return res


if __name__ == '__main__':
    m = 30
    p1 = 0.3
    reality = Reality(m=m)
    individual = Individual(m=m, p1=p1, reality=reality)
    print(individual.payoff)

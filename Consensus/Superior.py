# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import math
from Individual import Individual
import numpy as np
from Reality import Reality


class Superior:
    def __init__(self, m=None, s=None, t=None, n=None, reality=None, confirm=True):
        self.m = m  # state length
        self.s = s  # lower-level interdependency
        self.t = t  # upper-level interdependency
        self.n = n  # the number of subunits under this superior
        self.policy_num = self.m // self.s
        self.policy = np.random.choice([-1, 1], self.policy_num, p=[0.5, 0.5])
        self.individuals = []
        self.beliefs = []
        for _ in range(self.n):
            individual = Individual(m=self.m, s=self.s, t=self.t, reality=reality)
            if confirm:
                individual.confirm_to_supervision(policy=self.policy)
            self.individuals.append(individual)
            self.beliefs.append(individual.belief)
        self.reality = reality
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)

    def local_search(self):
        """
        Superior can do a free local search
        """
        focal_index = np.random.randint(0, self.policy_num)
        next_policy = self.policy.copy()
        if next_policy[focal_index] == 0:
            next_policy[focal_index] = np.random.choice([-1, 1])
        else:
            next_policy[focal_index] *= -1
        next_payoff = self.reality.get_policy_payoff(policy=next_policy)
        if next_payoff > self.payoff:
            self.policy = next_policy
            self.payoff = next_payoff
            for individual in self.individuals:
                individual.constrained_local_search(focal_policy=self.policy[focal_index], focal_policy_index=focal_index)

    def get_diversity(self):
        belief_pool = [individual.belief for individual in self.individuals]
        diversity = 0
        for individual in self.individuals:
            one_pair_diversity = [self.get_distance(individual.belief, belief_b) for belief_b in belief_pool]
            diversity += sum(one_pair_diversity)
        return diversity / self.n / self.n / self.m

    def get_distance(self, a=None, b=None):
        acc = 0
        for i in range(self.m):
            if a[i] * b[i] == -1:
                acc += 1
        return acc


if __name__ == '__main__':
    m = 27
    s = 1
    t = 3
    n = 4
    alpha = 0.5
    reality = Reality(m=m, s=s, t=t)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, confirm=True)
    for _ in range(100):
        superior.local_search()
        print(superior.payoff)
        # print("*"*10)
    # superior.describe()
    # truth_payoff = reality.get_policy_payoff(policy=reality.real_policy)
    # truth_payoff = reality.get_policy_payoff(policy=reality.real_policy)
    # print("The truth payoff is: ", truth_payoff)
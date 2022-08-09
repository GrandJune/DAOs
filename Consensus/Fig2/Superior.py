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
    def __init__(self, m=None, s=None, t=None, n=None, reality=None):
        self.m = m  # state length
        self.s = s  # lower-level interdependency
        self.t = t  # upper-level interdependency
        self.n = n  # the number of subunits under this superior
        self.policy_num = self.m // self.s
        self.policy = np.random.choice([-1, 1], self.policy_num, p=[0.5, 0.5])
        self.individuals = []
        for i in range(self.n):
            individual = Individual(m=self.m, s=self.s, t=self.t, reality=reality)
            individual.confirm_to_supervision(policy=self.policy)
            self.individuals.append(individual)
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
        whole_pool = [individual.belief for individual in self.individuals]
        pair_wise_diversity = [self.get_pair_distance(individual.belief, whole_pool)
                               for individual in self.individuals]
        return sum(pair_wise_diversity) / self.n

    def get_pair_distance(self, a=None, belief_pool=None):
        distance = 0
        for belief in belief_pool:
            acc = 0
            for i in range(self.m):
                if a[i] == belief[i]:
                    acc += 1
            distance += acc
        return distance / self.m



if __name__ == '__main__':
    m = 27
    s = 1
    t = 3
    n = 4
    alpha = 0.5
    reality = Reality(m=m, s=s, t=t, alpha=alpha)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
    for _ in range(100):
        superior.local_search()
        print(superior.payoff)
        # print("*"*10)
    # superior.describe()
    # truth_payoff = reality.get_policy_payoff(policy=reality.real_policy)
    # truth_payoff = reality.get_policy_payoff(policy=reality.real_policy)
    # print("The truth payoff is: ", truth_payoff)
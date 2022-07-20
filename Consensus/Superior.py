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
    def __init__(self, m=None, s=None, t=None, n=None, reality=None, alpha=None):
        self.m = m  # state length
        self.s = s  # lower-level interdependency
        self.t = t  # upper-level interdependency
        self.n = n  # the number of subunits under this superior
        self.policy_num = math.ceil(self.m / self.s)
        self.policy = np.random.choice([-1, 0, 1], self.policy_num, p=[1/3, 1/3, 1/3])
        self.individuals = []
        self.beliefs = []
        for i in range(self.n):
            individual = Individual(m=self.m, s=self.s, t=self.t, reality=reality)
            individual.confirm_to_supervision(policy=self.policy)
            self.individuals.append(individual)
            self.beliefs.append(individual.belief)
        self.reality = reality
        self.payoff = self.reality.get_hierarchy_payoff(alpha=alpha, policy=self.policy, beliefs=self.beliefs)

    def local_search(self, alpha=None):
        """
        Superior can do a free local search
        """
        focal_index = np.random.randint(0, self.policy_num)
        next_policy = self.policy.copy()
        if next_policy[focal_index] == 0:
            next_policy[focal_index] = np.random.choice([-1, 1])
        else:
            next_policy[focal_index] *= -1
        # the subunits need to confirm to the new policy
        for individual in self.individuals:
            individual.constrained_local_search(focal_policy=next_policy[focal_index], focal_policy_index=focal_index)
            self.beliefs = [individual.belief for individual in self.individuals]
        next_payoff = self.reality.get_hierarchy_payoff(alpha=alpha, policy=next_policy, beliefs=self.beliefs)
        print("The current policy is: ", self.payoff)
        print("The next payoff is: ", next_payoff)
        if next_payoff > self.payoff:
            self.policy = next_policy
            self.payoff = next_payoff
        else:
            for individual in self.individuals:
                individual.roll_back()

    def describe(self):
        print("The policy is: ", self.policy)
        print("The payoff is: ", self.payoff)
        print("The individuals are: ")
        # for individual in self.individuals:
        #     individual.describe()
        print("The beliefs are: ")
        for belief in self.beliefs:
            print(belief)
        print("The reality is: ", self.reality.real_code, self.reality.real_policy)


if __name__ == '__main__':
    m = 27
    s = 3
    t = 3
    n = 4
    alpha = 0.5
    reality = Reality(m=m, s=s, t=t, alpha=alpha)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, alpha=alpha)
    for _ in range(100):
        superior.local_search()
        print("*"*10)
    # superior.describe()
    truth_payoff = reality.get_hierarchy_payoff(alpha=alpha, policy=reality.real_policy, beliefs=[reality.real_code])
    print("The truth payoff is: ", truth_payoff)
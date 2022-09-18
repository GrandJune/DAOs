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
    def __init__(self, m=None, s=None, t=None, n=None, reality=None, authority=1.0):
        """
        :param m: problem space
        :param s: the first complexity
        :param t: the second complexity
        :param n: the number of agents
        :param reality: to provide feedback
        :param confirm: the extent to which agents confirm to their superior
        """
        self.m = m  # state length
        self.s = s  # lower-level interdependency
        self.n = n  # the number of subunits under this superior
        self.policy_num = self.m // self.s
        self.individuals = []
        self.belief_list = []
        self.belief = np.random.choice([-1, 0, 1], self.policy_num, p=[1/3, 1/3, 1/3])
        self.reality = reality
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        self.authority = authority
        for _ in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=reality)
            if self.authority:
                individual.confirm_to_supervision(policy=self.policy, authority=authority)
            self.individuals.append(individual)
            self.belief_list.append(individual.belief)
        self.payoff = self.reality.get_payoff(self.policy)

    def local_search(self):
        """
        Superior can do a free local search, and then agents adjust accordingly.
        """
        next_belief = self.belief.copy()
        focal_index = np.random.choice(self.m)
        if next_belief[focal_index] == 0:
            next_belief[focal_index] = np.random.choice([-1, 1])  # Another way is to make the knowledge scope fixed
            # return
        else:
            next_belief[focal_index] *= -1
        next_policy = self.reality.belief_2_policy(belief=next_belief)
        next_payoff = self.reality.get_payoff(belief=next_belief)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            self.policy = next_policy
        for individual in self.individuals:
            individual.constrained_local_search_under_authority(focal_policy=self.policy[focal_index],
                                                                focal_policy_index=focal_index, authority=self.authority)

    def weighted_local_search(self):
        """
        The strategic local search is based on weights across difference domains.
        """
        focal_index = np.random.choice(range(self.policy_num), p=self.reality.weight_list)
        next_policy = self.policy.copy()
        if next_policy[focal_index] == 0:
            next_policy[focal_index] = np.random.choice([-1, 1])
        else:
            next_policy[focal_index] *= -1
        next_payoff = self.reality.get_payoff(next_policy)
        if next_payoff > self.payoff:
            self.policy = next_policy
            self.payoff = next_payoff
        for individual in self.individuals:
            individual.constrained_local_search_under_authority(focal_policy=self.policy[focal_index],
                                                            focal_policy_index=focal_index, authority=self.authority)

    def random_guess(self):
        focal_index = np.random.randint(0, self.policy_num)
        next_policy = self.policy.copy()
        if next_policy[focal_index] == 0:
            next_policy[focal_index] = np.random.choice([-1, 1])
        else:
            next_policy[focal_index] *= -1
        next_payoff = self.reality.get_policy_payoff(policy=next_policy)
        self.policy = next_policy
        self.payoff = next_payoff
        for individual in self.individuals:
            individual.constrained_local_search_under_authority(focal_policy=self.policy[focal_index], focal_policy_index=focal_index, authority=self.authority)

    def get_diversity(self):
        belief_pool = [individual.belief for individual in self.individuals]
        diversity = 0
        for index, individual in enumerate(self.individuals):
            selected_pool = belief_pool[index+1::]
            one_pair_diversity = [self.get_distance(individual.belief, belief) for belief in selected_pool]
            diversity += sum(one_pair_diversity)
        return diversity / self.m / (self.n - 1) / self.n * 2

    def get_distance(self, a=None, b=None):
        acc = 0
        for i in range(self.m):
            if a[i] != b[i]:
                acc += 1
        return acc


if __name__ == '__main__':
    m = 27
    s = 3
    t = 1
    n = 10
    authority = 0.8
    reality = Reality(m=m, s=s, t=t)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    # for _ in range(100):
    #     superior.local_search()
    #     print(superior.payoff)
        # print("*"*10)
    # superior.describe()
    # truth_payoff = reality.get_policy_payoff(policy=reality.real_policy)
    # truth_payoff = reality.get_policy_payoff(policy=reality.real_policy)
    # print("The truth payoff is: ", truth_payoff)
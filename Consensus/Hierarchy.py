# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual import Individual
import numpy as np
from Reality import Reality
from Superior import Superior


class Hierarchy:
    def __init__(self, m=None, s=None, n=None, reality=None, lr=0.3):
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
        if self.m % self.s != 0:
            raise ValueError("m is not dividable by s")
        self.policy_num = self.m // self.s
        self.lr = lr
        self.reality = reality
        self.superior = Superior(m=self.policy_num, reality=self.reality, n=50)
        self.individuals = []
        self.belief = np.random.choice([-1, 0, 1], self.policy_num, p=[1/3, 1/3, 1/3])
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        self.authority = authority  # agent learning from authority code/policy
        for _ in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=self.reality, lr=self.lr)
            self.individuals.append(individual)

    def search(self):
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

    def random_supervision(self):
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
    lr = 0.3  # agent learning from code
    authority = 0.8
    reality = Reality(m=m, s=s)
    superior = Hierarchy(m=m, s=s, n=n, reality=reality, authority=authority, lr=lr)
    # for _ in range(100):
    #     superior.local_search()
    #     print(superior.payoff)
        # print("*"*10)
    # superior.describe()
    # truth_payoff = reality.get_policy_payoff(policy=reality.real_policy)
    # truth_payoff = reality.get_policy_payoff(policy=reality.real_policy)
    # print("The truth payoff is: ", truth_payoff)
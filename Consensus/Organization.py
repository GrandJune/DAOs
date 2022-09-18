# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import math
from Individual import Individual
from Superior import Superior
import numpy as np
from Reality import Reality


class Organization:
    def __init__(self, m=None, s=None, n=None, reality=None, authority=1.0):
        """
        :param m: problem space
        :param s: the first complexity
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
        self.reality = reality
        self.consensus = [0] * (m // s)
        for _ in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=self.reality)
            self.individuals.append(individual)
            self.belief_list.append(individual.belief)
        self.performance_across_time = []
        self.diversity_across_time = []

    def search(self):
        for individual in self.individuals:
            next_index = np.random.choice(len(self.consensus))
            next_policy = self.consensus[next_index]
            individual.constrained_local_search_under_consensus(focal_policy=next_policy, focal_policy_index=next_index)
        consensus = []
        for i in range(m//s):
            temp = sum(individual.policy[i] for individual in self.individuals)
            if temp < 0:
                consensus.append(-1)
            elif temp > 0:
                consensus.append(1)
            else:
                consensus.append(0)
        self.consensus = consensus.copy()
        performance_list = [individual.payoff for individual in self.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.diversity_across_time.append(self.get_diversity())

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
    n = 50
    reality = Reality(m=m, s=s, t=t)
    organization = Organization(m=m, s=s, n=n, reality=reality)
    for _ in range(300):
        organization.search()
    import matplotlib.pyplot as plt
    x = range(300)
    plt.plot(x, organization.performance_across_time, "k-", label="DAO")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Diversity_Comparison_s3.png", transparent=True, dpi=1200)
    plt.show()
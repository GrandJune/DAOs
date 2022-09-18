# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual import Individual
import numpy as np
from Reality import Reality


class Autonomy:
    def __init__(self, m=None, s=None, n=None, reality=None, subgroup_size=None, lr=None):
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
        self.subgroup_size = subgroup_size
        if self.n % self.subgroup_size != 0:
            raise ValueError("N must be divisible by subgroup size")
        self.group_num = self.s // self.subgroup_size
        self.policy_num = self.m // self.s
        self.individuals = []
        self.reality = reality
        for i in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=self.reality)
            individual.connections = list(range((i // self.subgroup_size) * self.subgroup_size, ((i // self.subgroup_size) + 1) * self.subgroup_size))
            self.individuals.append(individual)

        self.lr = lr  # learning from code
        self.performance_across_time = []
        self.diversity_across_time = []


    def search(self):
        # For autonomy, only learn from an isolated subgroup, according to Fang (2010)'s paper
        for individual in self.individuals:
            connected_group = [self.individuals[i] for i in individual.connections]
            superior_belief = []
            for each in connected_group:
                if each.payoff > individual.payoff:
                    superior_belief.append(each.belief)
            if len(superior_belief) != 0:
                majority_view = self.get_majority_view(superior_belief)
                for i in range(self.m):
                    if np.random.uniform(0, 1) < self.lr:
                        individual.belief[i] = majority_view[i]
                individual.payoff = self.reality.get_payoff(belief=individual.belief)
            # else:
            #     print(individual.payoff)
        performance_list = [individual.payoff for individual in self.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.diversity_across_time.append(self.get_diversity())

    def get_majority_view(self, superior_belief=None):
        majority_view = []
        for i in range(self.m):
            temp = [belief[i] for belief in superior_belief]
            if sum(temp) > 0:
                majority_view.append(1)
            elif sum(temp) < 0:
                majority_view.append(-1)
            else:
                majority_view.append(0)
        return majority_view

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
    n = 200
    group_size = 20
    lr = 0.3
    reality = Reality(m=m, s=s)
    organization = Autonomy(m=m, s=s, n=n, subgroup_size=group_size, reality=reality, lr=lr)
    for _ in range(100):
        organization.search()
    import matplotlib.pyplot as plt
    x = range(100)
    plt.plot(x, organization.performance_across_time, "k-", label="Autonomy")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Diversity_Comparison_s3.png", transparent=True, dpi=1200)
    plt.show()
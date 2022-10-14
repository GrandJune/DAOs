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
    def __init__(self, m=None, s=None, n=None, reality=None, lr=None, subgroup_size=None):
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
        self.policy_num = self.m // 3
        self.lr = lr  # learning rate
        self.subgroup_size = subgroup_size
        self.reality = reality
        self.superior = Superior(m=self.policy_num, reality=self.reality, n=50, p1=0.9, p2=0.1)
        # n is the number of managers, instead of employers;  In March's paper, n=50
        # p1, p2 is set to be the best one in March's paper
        self.individuals = []
        for i in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=self.reality, lr=self.lr)
            individual.connections = list(range((i // self.subgroup_size) * self.subgroup_size, ((i // self.subgroup_size) + 1) * self.subgroup_size))
            self.individuals.append(individual)
        # DVs
        self.performance_across_time = []
        self.deviation_across_time = []
        self.diversity_across_time = []
        self.superior_performance_across_time = []

    def search(self):
        # Supervision Formation
        self.superior.search()
        # Autonomous team learning
        for individual in self.individuals:
            connected_group = [self.individuals[i] for i in individual.connections]
            superior_belief_pool = []
            for each in connected_group:
                if each.payoff > individual.payoff:
                    superior_belief_pool.append(each.belief)
            if len(superior_belief_pool) != 0:
                majority_view = self.get_majority_view(superior_belief_pool)
                individual.superior_majority_view = majority_view
            else:
                individual.superior_majority_view = None
        # Adjust the superior majority view according to supervision and then learn from it
        for individual in self.individuals:
            if individual.superior_majority_view:  # only those have better reference will learn / update their belief
                individual.superior_majority_view = \
                    self.adjust_majority_view(majority_view=individual.superior_majority_view)
                individual.learning_from_belief(belief=individual.superior_majority_view)
        performance_list = [individual.payoff for individual in self.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.deviation_across_time.append(np.std(performance_list))
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
        diversity = 0
        belief_pool = [individual.belief for individual in self.individuals]
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

    def adjust_majority_view(self, majority_view=None):
        adjusted_majority_view = majority_view.copy()
        if len(adjusted_majority_view) != self.m:
            raise ValueError("The length of majority view should be m")
        for index in range(self.policy_num):
            if sum(adjusted_majority_view[index*3: (index+1)*3]) != self.superior.policy[index]:
                adjusted_majority_view[index * 3: (index + 1) * 3] = self.reality.policy_2_belief(policy=self.superior.policy[index])
        return adjusted_majority_view


if __name__ == '__main__':
    m = 30
    s = 1
    n = 280
    lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, s=s)
    hierarchy = Hierarchy(m=m, s=s, n=n, reality=reality, lr=lr,subgroup_size=group_size)
    for _ in range(100):
        hierarchy.search()
    import matplotlib.pyplot as plt
    x = range(100)
    plt.plot(x, hierarchy.performance_across_time, "k-", label="Hierarchy")
    plt.plot(x, hierarchy.superior.performance_across_time, "k--", label="Superior")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("Hierarchy_performance.png", transparent=True, dpi=1200)
    plt.show()
    plt.clf()





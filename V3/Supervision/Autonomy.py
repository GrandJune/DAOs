# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual import Individual
import numpy as np
import math
from Reality import Reality
from Team import Team


class Autonomy:
    def __init__(self, m=None, s=None, n=None, reality=None, group_size=None, lr=None):
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
        self.reality = reality
        self.group_size = group_size
        self.lr = lr  # learning rate; learn from majority view
        if self.n % self.group_size != 0:
            raise ValueError("N must be divisible by subgroup size")
        if self.m % self.s != 0:
            raise ValueError("m is not dividable by s")
        self.policy_num = self.m // self.s
        self.teams = []
        for i in range(self.n // self.group_size):
            team = Team(m=self.m, index=i, policy_num=self.policy_num, reality=self.reality)
            for _ in range(self.group_size):
                individual = Individual(m=self.m, s=self.s, reality=self.reality, lr=self.lr)
                team.individuals.append(individual)
            # team.get_policy(token=False)  # No need for team policy; they do not coordinate
            self.teams.append(team)
        self.performance_across_time = []
        self.diversity_across_time = []

    def search(self):
        # For autonomy, only learn from an isolated subgroup, according to Fang (2010)'s paper
        # Autonomous team learning
        for team in self.teams:
            team.get_majority_view()
            for individual in team.individuals:
                individual.learning_from_belief(belief=individual.superior_majority_view)
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]
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
        diversity = 0
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        belief_pool = [individual.belief for individual in individuals]
        for index, individual in enumerate(individuals):
            selected_pool = belief_pool[index + 1::]
            one_pair_diversity = [self.get_distance(individual.belief, belief) for belief in selected_pool]
            diversity += sum(one_pair_diversity)
        return diversity / self.m / (self.n - 1) / self.n * 2

    def get_distance(self, a=None, b=None):
        acc = 0
        for i in range(self.m):
            if a[i] != b[i]:
                acc += 1
        return acc

    def turnover(self, turnover_rate=None):
        if turnover_rate:
            for team in self.teams:
                for individual in team.individuals:
                    if np.random.uniform(0, 1) < turnover_rate:
                        individual.turnover()


if __name__ == '__main__':
    m = 60
    s = 1
    n = 280
    lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    # according to the practice, such a subdivision of an organization, such a size of autonomous team cannot be large.
    reality = Reality(m=m, s=s)
    autonomy = Autonomy(m=m, s=s, n=n, group_size=group_size, reality=reality, lr=lr)
    for period in range(50):
        autonomy.search()
        print(period)
    import matplotlib.pyplot as plt
    x = range(50)
    plt.plot(x, autonomy.performance_across_time, "k-", label="Autonomy")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("Autonomy_performance.png", transparent=True, dpi=1200)
    plt.show()
    print("END")


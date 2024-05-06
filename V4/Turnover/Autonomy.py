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
    def __init__(self, m=None, n=None, reality=None, group_size=None, lr=None, alpha=3):
        """
        :param m: problem space
        :param n: the number of agents
        :param reality: to provide feedback
        :param confirm: the extent to which agents confirm to their superior
        """
        self.m = m  # state length
        self.n = n  # the number of subunits under this superior
        self.reality = reality
        self.group_size = group_size
        self.lr = lr  # learning rate; learn from majority view
        if self.n % self.group_size != 0:
            raise ValueError("N must be divisible by subgroup size")
        self.alpha = alpha
        self.policy_num = self.m // self.alpha
        self.teams = []
        for i in range(self.n // self.group_size):
            team = Team(m=self.m, index=i, alpha=self.alpha, reality=self.reality)
            for _ in range(self.group_size):
                individual = Individual(m=self.m, reality=self.reality, lr=self.lr, alpha=self.alpha)
                team.individuals.append(individual)
            self.teams.append(team)
        self.performance_across_time = []
        self.diversity_across_time = []
        self.variance_across_time = []

    def search(self):
        # For autonomy, only learn from an isolated subgroup, according to Fang (2010)'s paper
        # Autonomous team learning
        for team in self.teams:
            team.form_individual_majority_view()
            team.learn()
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
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
                    individual.turnover(turnover_rate=turnover_rate)


if __name__ == '__main__':
    m = 60
    s = 1
    n = 350
    lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    # according to the practice, such a subdivision of an organization, such a size of autonomous team cannot be large.
    reality = Reality(m=m, s=s)
    autonomy = Autonomy(m=m, s=s, n=n, group_size=group_size, reality=reality, lr=lr)
    for period in range(100):
        autonomy.search()
        print(period)
    import matplotlib.pyplot as plt

    x = range(100)
    plt.plot(x, autonomy.performance_across_time, "k-", label="Autonomy")
    plt.title('Performance')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("Autonomy_performance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, autonomy.diversity_across_time, "k-", label="Mean")
    plt.title('Diversity')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("Autonomy_diversity.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, autonomy.variance_across_time, "k-", label="Autonomy")
    plt.title('Variance')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("Autonomy_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    print("END")



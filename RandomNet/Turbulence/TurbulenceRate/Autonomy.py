# -*- coding: utf-8 -*-
# @Time     : 24/01/2024 19:05
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
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size=None,
                 alpha=3):
        """
        :param m: problem space
        :param n: the number of agents
        :param reality: to provide feedback
        """
        self.m = m  # state length
        self.n = n  # the number of subunits under this superior
        self.alpha = alpha  # The aggregation degree
        self.policy_num = self.m // self.alpha
        self.reality = reality
        self.lr = lr  # learning from consensus
        self.group_size = group_size
        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.individuals = []
        for i in range(self.n):
            individual = Individual(m=self.m, alpha=self.alpha, reality=self.reality, lr=self.lr)
            self.individuals.append(individual)
        self.form_network()
        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []

    def form_network(self):
        for individual in self.individuals:
            individual.connections = np.random.choice(range(self.n), self.group_size, replace=False)

    def search(self):
        for individual in self.individuals:
            # 1) Generate Pure Majority View
            others_belief_pool = []
            for connect in individual.connections:
                others_belief_pool.append(self.individuals[connect].belief)
            individual.form_superior_majority_view(superior_belief_pool=others_belief_pool)
            # 2) Learn From Majority View
            individual.learning_from_belief(belief=individual.superior_majority_view)
        performance_list = [individual.payoff for individual in self.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())

    def get_diversity(self):
        diversity = 0
        belief_pool = [individual.belief for individual in self.individuals]
        for index, individual in enumerate(self.individuals):
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
            for individual in self.individuals:
                individual.turnover(turnover_rate=turnover_rate)


if __name__ == '__main__':
    m = 60
    s = 1
    n = 350
    lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    # according to the practice, such a subdivision of an organization, such a size of autonomous team cannot be large.
    reality = Reality(m=m)
    autonomy = Autonomy(m=m, n=n, group_size=group_size, reality=reality, lr=lr)
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
    # plt.savefig("Autonomy_performance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, autonomy.diversity_across_time, "k-", label="Mean")
    plt.title('Diversity')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Autonomy_diversity.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, autonomy.variance_across_time, "k-", label="Autonomy")
    plt.title('Variance')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Autonomy_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    print("END")



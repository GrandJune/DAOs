# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual import Individual
from Reality import Reality


class DAO:
    def __init__(self, m=None, s=None, n=None, reality=None, lr=0.3):
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
        if self.m % self.s != 0:
            raise ValueError("m is not dividable by s")
        self.policy_num = self.m // self.s
        self.individuals = []
        self.reality = reality
        self.lr = lr
        self.consensus = [0] * (m // s)
        for _ in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=self.reality, lr=self.lr)
            self.individuals.append(individual)
        self.performance_across_time = []
        self.diversity_across_time = []

    def search(self):
        for individual in self.individuals:
            individual.learning_from_consensus(consensus=self.consensus)
        new_consensus = []
        for i in range(m//s):
            temp = sum(individual.policy[i] for individual in self.individuals)
            if temp < 0:
                new_consensus.append(-1)
            elif temp > 0:
                new_consensus.append(1)
            else:
                new_consensus.append(0)
        self.consensus = new_consensus.copy()
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
    n = 200
    lr = 0.3
    reality = Reality(m=m, s=s)
    organization = DAO(m=m, s=s, n=n, reality=reality, lr=lr)
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
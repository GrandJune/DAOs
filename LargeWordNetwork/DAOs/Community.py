# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 16:52
# @Author   : Junyi
# @FileName: Community.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Organization import Organization
from Individual import Individual
from Reality import Reality
import multiprocessing as mp


class Community:
    def __init__(self, m=None, s=None, n=None, size=None,
                 reality=None, beta=None, lr=None):
        self.m = m
        self.s = s
        self.n = n
        self.size = size
        self.individuals = []
        self.clusters = []
        self.code_list = []
        self.reality = reality
        self.cluster_num = self.n // self.size
        self.beta = beta
        self.lr = lr
        # DV
        self.performance_curve_cluster = []
        self.performance_curve_individual = []
        self.performance_average_cluster = []
        self.performance_average_individual = []

    def initialize(self):
        for i in range(self.cluster_num):
            cluster = Organization(m=self.m, s=self.s, beta=self.beta, reality=self.reality, index=i)
            self.clusters.append(cluster)
            self.code_list.append(cluster.code)
        for i in range(self.n):
            individual = Individual(m=m, s=s, reality=self.reality, index=i, lr=self.lr, beta=self.beta)
            self.individuals.append(individual)
        for individual in self.individuals:
            individual.cluster = self.get_cluster(belief=individual.belief, code_list=self.code_list)

    def get_cluster(self, belief=None, code_list=None):
        sum_list = []
        for index, code in enumerate(code_list):
            sum_list.append(sum([a*b for a, b in zip(belief, code)]))
        return sum_list.index(max(sum_list))

    def get_cluster_code(self, index=None):
        belief_pool = []
        dominant_belief = []
        for individual in self.individuals:
            if individual.cluster == index:
                belief_pool.append(individual.belief)
        for dimension in range(self.m):
            temp = sum([belief[dimension] for belief in belief_pool])
            if temp > 0:
                dominant_belief.append(1)
            elif temp < 0:
                dominant_belief.append(-1)
            else:
                dominant_belief.append(0)
        return dominant_belief

    def process(self):
        for individual in self.individuals:
            individual.local_search()
        for cluster in self.clusters:
            cluster.code = self.get_cluster_code(index=cluster.index)
            self.code_list.append(cluster.code)
        for individual in self.individuals:
            individual.learn(code=self.code_list[individual.cluster])
        # reassign the cluster
        for individual in self.individuals:
            if np.random.uniform(0, 1) < self.beta:
                individual.cluster = self.get_cluster(belief=individual.belief, code_list=self.code_list)
        payoff_cluster = [self.reality.get_payoff(belief=cluster.code) for cluster in self.clusters]
        payoff_individual = [self.reality.get_payoff(belief=individual.belief) for individual in self.individuals]
        self.performance_average_cluster = sum(payoff_cluster) / len(payoff_cluster)
        self.performance_average_individual = sum(payoff_individual) / len(payoff_individual)
        self.performance_curve_cluster.append(self.performance_average_cluster)
        self.performance_curve_individual.append(self.performance_average_individual)

    def describe(self):
        cluster_range = list(range(self.cluster_num))
        size_count = [0] * self.cluster_num
        for individual in self.individuals:
            size_count[individual.cluster] += 1
        plt.bar(cluster_range, size_count, fc='k')
        plt.xlabel("Cluster")
        plt.ylabel("Size")
        plt.show()


def func(m=None, s=None, beta=None, lr=None, n=None, size=None):
    reality = Reality(m=m, s=s)
    community = Community(m=m, s=s, n=n, size=size, reality=reality, lr=lr, beta=beta)
    community.initialize()
    loop = 800
    for _ in range(loop):
        community.process()
    plt.plot(range(loop), community.performance_curve_cluster, 'k-', label='Cluster')
    plt.plot(range(loop), community.performance_curve_individual, "k:", label='Individual')
    plt.xlabel('Iteration')
    plt.ylabel('Performance')
    plt.legend()
    plt.savefig("Curve_m{0}_s{1}_beta{2}_lr_{3}.jpg".format(m, s, beta, lr))


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # m = 10
    # s = 1
    n = 1000
    size = 50
    # loop = 100
    # lr = 0.3
    # beta = 0.5
    for m in [100]:
        for s in [1, 2, 5]:
            for beta in [0, 0.3, 1]:
                for lr in [0, 0.3, 1]:
                    p = mp.Process(target=func, args=(m, s, beta, lr, n, size))
                    p.start()

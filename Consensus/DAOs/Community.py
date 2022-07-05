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
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt



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
        # Network
        self.individual_2_cluster = []  # get the individuals' belonging [i1, 12, ..., ]
        self.cluster_2_individual = []  # get the clusters' substance [c1: [], c2: [], ...]
        self.individual_2_individual = [[0]] * self.n  # get the individuals' links to other individual [i1: [], i2: [], ...]

        # DV
        self.performance_curve_cluster = []
        self.performance_curve_individual = []
        self.performance_average_cluster = []
        self.performance_average_individual = []
        self.code_evolution_list = []

    def initialize(self):
        """
        Build the network architecture
        """
        # initialize the cluster
        for i in range(self.cluster_num):
            cluster = Organization(m=self.m, s=self.s, beta=self.beta, reality=self.reality, index=i)
            self.clusters.append(cluster)
            self.code_list.append(cluster.code)
        # initialize the individual, and randomly assign the belonging
        for i in range(self.n):
            individual = Individual(m=m, s=s, reality=self.reality, index=i, lr=self.lr, beta=self.beta)
            self.individuals.append(individual)
            self.individual_2_cluster.append(np.random.choice(range(self.cluster_num)))
        # record the clusters' substance
        self.update_cluster_substance()
        # build the individuals' network
        self.update_individual_network()

    def update_cluster_substance(self):
        self.cluster_2_individual = []
        for cluster_index in range(self.cluster_num):
            temp = [individual for individual, cluster in
                    enumerate(self.individual_2_cluster) if cluster == cluster_index]
            self.cluster_2_individual.append(temp)

    def update_individual_network(self):
        self.individual_2_individual = [[]] * self.n
        for cluster_substance in self.cluster_2_individual:
            for individual_index in range(self.n):
                if individual_index in cluster_substance:
                    self.individual_2_individual[individual_index] = cluster_substance.copy()

    def remain_superior_link(self):
        """
        Extension
        When individuals change the relationship, maintain one link that performs best.
        :return:
        """
        pass

    def get_cluster(self, belief=None, code_list=None):
        sum_list = []
        for index, code in enumerate(code_list):
            sum_list.append(sum([a*b for a, b in zip(belief, code)]))
        max_value = max(sum_list)
        max_index = [index for index, value in enumerate(sum_list) if value == max_value]
        return np.random.choice(max_index)

    def get_cluster_code_majority(self, index=None):
        """
        form the majority code for the specific cluster (index)
        :param index: the cluster index
        :return: the cluster code
        """
        belief_pool = []
        # using the cluster code as the default (no information gain)
        dominant_belief = self.clusters[index].code.copy()
        for individual in self.individuals:
            if individual.index in self.cluster_2_individual[index]:
                belief_pool.append(individual.belief)
        for dimension in range(self.m):
            temp = sum([belief[dimension] for belief in belief_pool])
            if temp > 0:
                dominant_belief[dimension] = 1
            elif temp < 0:
                dominant_belief[dimension] = -1
            else:
                pass  # remain the previous code (no information gain)
        return dominant_belief

    def process(self):
        # individual search
        for individual in self.individuals:
            individual.local_search()
        # Reset the code list
        self.code_list = []
        # update the cluster code
        for cluster in self.clusters:
            cluster.code = self.get_cluster_code_majority(index=cluster.index)
            cluster.payoff = self.reality.get_payoff(belief=cluster.code)
            self.code_list.append(cluster.code)
        # learn from the code
        for individual in self.individuals:
            individual.learn_from_code(code=self.code_list[self.individual_2_cluster[individual.index]])
        # learn from the peer
        for individual in self.individuals:
            # using the personal belief as the default (no information gain)
            superior_belief = individual.belief.copy()
            focal_superior_beliefs = []
            # print(self.individual_2_individual[individual.index])
            for index in self.individual_2_individual[individual.index]:
                if self.individuals[index].payoff > individual.payoff:
                    focal_superior_beliefs.append(self.individuals[index].belief)
            for dimension in range(self.m):
                temp = sum([belief[dimension] for belief in focal_superior_beliefs])
                if temp > 0:
                    superior_belief[dimension] = 1
                elif temp < 0:
                    superior_belief[dimension] = -1
                else:pass  # for zero, remain uncertain
            individual.superior_belief = superior_belief
        for individual in self.individuals:
            individual.learn_from_peers()

        # reassign the cluster
        for index in range(self.n):
            if np.random.uniform(0, 1) < self.beta:
                self.individual_2_cluster[index] = self.get_cluster(belief=self.individuals[index].belief, code_list=self.code_list)
        self.update_cluster_substance()
        self.update_individual_network()
        payoff_cluster = [self.reality.get_payoff(belief=cluster.code) for cluster in self.clusters]
        payoff_individual = [self.reality.get_payoff(belief=individual.belief) for individual in self.individuals]
        self.performance_average_cluster = sum(payoff_cluster) / len(payoff_cluster)
        self.performance_average_individual = sum(payoff_individual) / len(payoff_individual)
        self.performance_curve_cluster.append(self.performance_average_cluster)
        self.performance_curve_individual.append(self.performance_average_individual)

        self.code_evolution_list.append(self.code_list)

    def describe(self):
        cluster_range = list(range(self.cluster_num))
        size_count = [0] * self.cluster_num
        # for individual in self.individuals:
        #     size_count[individual.cluster] += 1
        for index, value in enumerate(self.cluster_2_individual):
            size_count[index] += len(value)
        plt.bar(cluster_range, size_count, fc='k')
        plt.xlabel("Cluster")
        plt.ylabel("Size")
        plt.savefig("Distribution_m{0}_s{1}_beta{2}_lr{3}.jpg".format(self.m, self.s, self.beta, self.lr))
        # plt.show()
        # print("Sum: ", sum(size_count))


def func(m=None, s=None, beta=None, lr=None, n=None, size=None, loop=None):
    reality = Reality(m=m, s=s)
    community = Community(m=m, s=s, n=n, size=size, reality=reality, lr=lr, beta=beta)
    community.initialize()
    # community.describe()
    for _ in range(loop):
        community.process()
    plt.plot(range(loop), community.performance_curve_cluster, 'k-', label='Cluster')
    plt.plot(range(loop), community.performance_curve_individual, "k:", label='Individual')
    plt.xlabel('Iteration')
    plt.ylabel('Performance')
    plt.title("lr_{0}_beta_{1}".format(lr, beta))
    plt.legend()
    plt.savefig("m_{0}_s{1}_beta_{2}_lr_{3}.jpg".format(m, s, beta, lr))
    # plt.show()
    community.describe()
    print(m, s, beta, lr, "Individual: ", community.performance_average_individual)
    print(m, s, beta, lr, "Cluster: ", community.performance_average_cluster)




if __name__ == '__main__':
    # m = 100
    # s = 5
    n = 1000
    size = 20
    loop = 1000
    # lr = 0
    # beta = 0.5
    for m in [100]:
        for s in [1, 5, 10]:
            for beta in [0, 0.5, 1]:
                for lr in [0, 0.5, 1]:
                    p = mp.Process(target=func, args=(m, s, beta, lr, n, size, loop))
                    p.start()

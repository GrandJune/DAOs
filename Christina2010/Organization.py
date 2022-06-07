# -*- coding: utf-8 -*-
# @Time     : 6/4/2022 16:17
# @Author   : Junyi
# @FileName: Organization.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality
from Individual import Individual
import math


class Organization:
    def __init__(self, n=None, beta=None, subgroup_size=None, m=None, s=None,
                 reality=None, lr=None, turnover_rate=None, reality_change_rate=None):
        self.n = n
        # Beta: the fraction of additional cross-group links
        self.beta = beta
        self.subgroup_size = subgroup_size
        self.m = m
        self.s = s
        self.reality = reality
        self.individuals = []
        self.lr = lr  # learning rate
        self.turnover_rate = turnover_rate  # turnover rate
        self.reality_change_rate = reality_change_rate  # change the real code
        for i in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=self.reality, lr=self.lr)
            individual.index = i
            individual.cluster = i // self.subgroup_size
            self.individuals.append(individual)

        # DV
        self.performance_average = 0
        self.performance_variance = 0



    def form_network(self):
        # connections within the cluster (minimal connectivity)
        for index, individual in enumerate(self.individuals):
            individual.connections = [0] * self.n
            # the range is [0, 50), [50, 100), etc.
            for link_index in range(individual.cluster * self.subgroup_size, (individual.cluster+1) * self.subgroup_size):
                individual.connections[link_index] = 1

        # Rewire the connection
        for individual in self.individuals:
            one_index = [index for index, value in enumerate(individual.connections) if value == 1]
            for index in one_index:
                if np.random.uniform(0, 1) < self.beta:
                    zero_index = [index for index, value in enumerate(individual.connections) if value == 0]
                    zero_index = [each for each in zero_index if each not in one_index]  # rule out the previous "one"
                    if len(zero_index) != 0:
                        selected_index = np.random.choice(zero_index, p=[1 / len(zero_index)] * len(zero_index))
                        individual.connections[selected_index] = 1
                        individual.connections[index] = 0

    def get_majority_view(self, individual=None):
        superior_group = []
        for connection in individual.connections:
            if self.individuals[connection].payoff > individual.payoff:
                superior_group.append(connection)
        majority_view = [1] * self.m
        for dimension in range(self.m):
            temp = 0
            for i in superior_group:
                temp += self.individuals[i].belief[dimension]
            if temp < 0:
                majority_view[dimension] = -1
        return majority_view

    def get_overall_similarity(self):
        """
        Dissimilarity Index
        :return:
        """
        distance = 0
        count = 0
        for i in range(self.n):
            for j in range(self.n):
                if i < j:
                    a = self.individuals[i]
                    b = self.individuals[j]
                    distance += self.get_distance(a.belief, b.belief)
                    count += 1
        return distance / count

    def get_distance(self, belief_1=None, belief_2=None):
        res = 0
        for i in range(self.m):
            if belief_1[i] == belief_2[i]:
                res += 1
        return res / self.m


    def process(self, loop=None, change_freq=None):
        for iteration in range(loop):
            # Search
            for individual in self.individuals:
                individual.local_search()
            # Learning
            for individual in self.individuals:
                majority_view = self.get_majority_view(individual=individual)
                # print("majority_view: ", majority_view)
                individual.learn(majority_view=majority_view)

            payoff_list = [individual.payoff for individual in self.individuals]
            self.performance_average = sum(payoff_list) / len(payoff_list)
            self.performance_variance = np.std(payoff_list)

            if self.turnover_rate:
                for individual in self.individuals:
                    if np.random.uniform(0, 1) < self.turnover_rate:
                        individual.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
                        individual.payoff = self.reality.get_payoff(belief=individual.belief)

            if iteration % change_freq == 0:
                self.reality.change(reality_change_rate=self.reality_change_rate)
                for individual in self.individuals:
                    individual.reality = self.reality
                    individual.payoff = self.reality.get_payoff(belief=individual.belief)

    def describe(self):
        print("-" * 10)
        print("n: {0}, size: {1}, m: {2}, s: {3}".format(self.n, self.subgroup_size, self.m, self.s))
        print("beta: ", self.beta)
        print("Real Belief: ", self.reality.real_code)
        print("Performance Average: ", self.performance_average)
        print("Performance Variance: ", self.performance_variance)
        print("-" * 10)


if __name__ == '__main__':
    n = 200
    beta = 0.1
    m = 10
    s = 1
    lr = 0
    subgroup_size = 50
    reality_change_rate = 0.1
    reality = Reality(m=m, s=s)
    organization = Organization(n=n, beta=beta, subgroup_size=subgroup_size, m=m, s=s, reality=reality,
                                lr=lr, reality_change_rate=reality_change_rate)
    organization.form_network()
    organization.individuals[0].describe()
    organization.process(loop=400, change_freq=200)
    organization.describe()





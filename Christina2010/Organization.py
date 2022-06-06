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
    def __init__(self, n=140, beta=0, subgroup_size=7, individuals=None):
        self.n = n
        # Beta: the fraction of additional cross-group links
        self.beta = beta
        self.subgroup_size = subgroup_size
        self.cluster_num = math.ceil(n / subgroup_size)
        self.individuals = individuals
        self.m = individuals[0].m
        self.s = individuals[0].s
        if len(individuals) != self.n:
            raise ValueError("Mismatch between n: {0} and length of individuals: {1}".format(self.n, len(self.individuals)))
        self.network = np.zeros(shape=(self.n, self.n))
        self.majority_view_list = []

    def form_network(self):
        # connections within the cluster (minimal connectivity)
        for i in range(self.cluster_num):
            row = i * self.subgroup_size
            for j in range(self.subgroup_size):
                column = j + row
                self.network[row][column] = 1
        # connections across clusters (additional connectivity)
        for i in range(self.n):
            if np.random.uniform(0, 1) < self.beta:
                free_space = np.array(np.where(self.network == 0))
                selected_space = np.random.choice(free_space, p=[1 / len(free_space)] * len(free_space))



    def get_similarity(self):
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



    def describe(self):
        print("n: ", self.n)
        print("subgroup size: ", self.subgroup_size)
        print("beta: ", self.beta)
        print("cluster number: ", self.cluster_num)
        print("network: ", self.network)



if __name__ == '__main__':
    n = 200
    beta = 0
    m = 40
    s = 4
    subgroup_size = 50
    reality = Reality(m=m, s=s)
    individuals = []
    for i in range(n):
        individual = Individual(m=m, s=s, reality=reality)
        individuals.append(individual)
    organization = Organization(n=n, beta=beta, individuals=individuals, subgroup_size=subgroup_size)
    organization.describe()





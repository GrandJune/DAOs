# -*- coding: utf-8 -*-
# @Time     : 6/23/2022 21:38
# @Author   : Junyi
# @FileName: Organization.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality
from Individual import Individual


class Organization:
    def __init__(self, m=None, n=None, p1=None, p2=None, reality=None):
        self.m = m
        self.n = n
        self.code =[0] * self.m
        self.p1 = p1  # belief learning from code
        self.p2 = p2  # code learning from beliefs
        self.reality = reality
        self.payoff = 0
        self.individuals = []
        for i in range(self.n):
            individual = Individual(index=i, m=self.m, p1=self.p1, reality=self.reality)
            self.individuals.append(individual)
        self.superior_group = []

        # DV
        self.performance_curve = []  # the evolution of performance
        self.performance_average = 0  # performance iteration

    def learn_from_beliefs(self):
        belief_list = [individual.belief for individual in self.individuals if individual.index in self.superior_group]
        dominant_belief = self.get_dominant_belif(belief_list=belief_list)
        for index in range(self.m):
            if np.random.uniform(0, 1) < self.p2:
                self.code[index] = dominant_belief[index]
        self.payoff = self.reality.get_payoff(belief=self.code)

    def get_superior_group(self):
        self.superior_group = []
        for individual in self.individuals:
            if individual.payoff > self.payoff:
                self.superior_group.append(individual.index)

    def get_dominant_belif(self, belief_list=None):
        res = [0] * self.m
        for index in range(self.m):
            temp = sum([each[index] for each in belief_list])
            if temp > 0:
                res[index] = 1
            elif temp < 0:
                res[index] = -1
        return res

    def personnel_turnover(self, p3=None):
        for individual in self.individuals:
            if np.random.uniform(0, 1) < p3:
                individual.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
                individual.payoff = self.reality.get_payoff(belief=individual.belief)

    def process(self, loop=100, p3=None, p4=None):
        for _ in range(loop):
            self.get_superior_group()
            # print(len(self.superior_group))
            self.learn_from_beliefs()  # update the organizational code and payoff
            for individual in self.individuals:
                individual.learn_from_code(code=self.code)  # update the individual belief and payoff
            if p3:
                self.personnel_turnover(p3=p3)
            if p4:
                change = self.reality.turbulence(p4=p4)
                if change:
                    self.payoff = self.reality.get_payoff(belief=self.code)
                    for individual in self.individuals:
                        individual.payoff = self.reality.get_payoff(belief=individual.belief)
            payoff_list = [individual.payoff for individual in self.individuals]
            self.performance_average = sum(payoff_list) / self.n
            self.performance_curve.append(self.performance_average)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    m = 30
    n = 100
    p1 = 0.3
    p2 = 0.3
    loop = 50
    reality = Reality(m=m)
    # individual = Individual(m=m, p1=p1, reality=reality)
    organization = Organization(m=m, n=n, p1=p1, p2=p2, reality=reality)
    organization.process(loop=loop)
    x = range(loop)
    plt.plot(x, organization.performance_curve, "k-")
    # plt.savefig("search.jpg")
    plt.title('Search Evolution')
    plt.xlabel('Time')
    plt.ylabel('Performance')
    plt.legend()
    plt.show()
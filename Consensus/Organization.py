# -*- coding: utf-8 -*-
# @Time     : 6/22/2022 15:07
# @Author   : Junyi
# @FileName: Organization.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality
from Individual import Individual


class Organization:
    def __init__(self, m=None, s=None, n=None, p1=None, p2=None, reality=None):
        self.m = m # State length
        self.s = s  # Complexity
        self.n = n # Agent number
        self.code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5]).tolist()
        self.p1 = p1  # learning from code
        self.p2 = p2  # learning from beliefs (herein the focal task scope)
        self.reality = reality
        self.individuals = []
        self.belief_pool = []
        self.payoff_pool = []
        for i in range(self.n):
            individual = Individual(index=i, m=self.m, p1=self.p1, reality=self.reality)
            self.individuals.append(individual)
            self.belief_pool.append(individual.belief)
            self.payoff_pool.append(individual.payoff)
        # previous view stands the organizational elitism (select the over-performance individuals as managers,
        # whose opinions are more rrepresentative of the organization)
        # our view stands the consensus based mechanism, which is the most important feature of the DAOs system
        # IV
        self.path_length = 0

        # DV
        self.performance_curve = []  # the evolution of performance
        self.performance_average = 0  # performance iteration


    def personnel_turnover(self, p3=None):
        for individual in self.individuals:
            if np.random.uniform(0, 1) < p3:
                individual.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
                individual.payoff = self.reality.get_payoff(belief=individual.belief)

    def process(self, loop=100, p3=None, p4=None, task_size=None):
        for _ in range(loop):
            task = self.reality.generate_task(task_size=task_size)
            # print("task:", task)
            self.get_superior_group(task=task)  # get the superior group for the task
            # print(len(self.superior_group))
            self.learn_from_beliefs(task=task)  # update the organizational code and payoff, based on task
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

    def get_dominant_belief(self):
        dominant_belief = []
        for index in range(self.m):
            temp = 0
            for individual in self.individuals:
                temp += individual.belief[index]
            if temp > 0:
                dominant_belief.append(1)
            elif temp < 0:
                dominant_belief.append(-1)
            else:
                dominant_belief.append(0)
        return dominant_belief


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    m = 30
    s = 2
    n = 5
    p1 = 0.3
    p2 = 0.5
    loop = 100
    task_size = 10
    reality = Reality(m=m, s=s)
    # individual = Individual(m=m, p1=p1, reality=reality)
    organization = Organization(m=m, s=s, n=n, p1=p1, p2=p2, reality=reality)
    organization.form_network(loop=loop)
    # organization.process(loop=loop, task_size=task_size)
    # x = range(loop)
    # plt.plot(x, organization.performance_curve, "k-")
    # # plt.savefig("search.jpg")
    # plt.title('Search Evolution')
    # plt.xlabel('Time')
    # plt.ylabel('Performance')
    # # plt.legend()
    # plt.show()
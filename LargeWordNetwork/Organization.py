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
        self.m = m
        self.s = s
        self.n = n
        self.code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5]).tolist()
        self.p1 = p1  # learning from code
        self.p2 = p2  # learning from beliefs (herein the focal task scope)
        self.reality = reality
        self.partial_payoff = 0
        self.individuals = []
        for i in range(self.n):
            individual = Individual(index=i, m=self.m, p1=self.p1, reality=self.reality)
            self.individuals.append(individual)
        self.superior_group = []  # change the definition of superior group
        # previous view stands the organizational elitism (select the over-performance individuals as managers,
        # whose opinions are more rrepresentative of the organization)
        # our view stands the consensus based mechanism, which is the most important feature of the DAOs system

        # DV
        self.performance_curve = []  # the evolution of performance
        self.performance_average = 0  # performance iteration

    def learn_from_beliefs(self, task=None):
        belief_list = [individual.belief for individual in self.individuals if individual.index in self.superior_group]
        dominant_belief = self.get_partial_dominant_belief(belief_list=belief_list, task=task)
        for index in range(self.m):
            if np.random.uniform(0, 1) < self.p2:
                self.code[index] = dominant_belief[index]

    def get_superior_group(self, task=None):
        """
        The task is to get the superior group of the organization.
        :param task: the index for the task location; limit the search scope
        :return: task-driven superior group
        """
        for individual in self.individuals:
            individual.partial_payoff = self.reality.get_partial_payoff(belief=individual.belief, task=task)
        self.partial_payoff = self.reality.get_partial_payoff(belief=self.code, task=task)
        self.superior_group = []
        for individual in self.individuals:
            if individual.partial_payoff > self.partial_payoff:
                self.superior_group.append(individual.index)

    def get_partial_dominant_belief(self, belief_list=None, task=None):
        """
        The organizational code will only learn from the focal task scope, while keeping the other elements unchanged.
        :param belief_list: the belief list from the focal superior group
        :param task: the focal task scope
        :return: the partial dominant belief, with same elements as the organizational code outside the focal task scope
        """
        res = self.code.copy()
        for index in task:
            temp = sum([each[index] for each in belief_list])
            if temp > 0:
                res[index] = 1
            elif temp < 0:
                res[index] = -1
            else:pass  # the organizational code remains unchanged
        return res

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


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    m = 30
    s = 2
    n = 100
    p1 = 0.3
    p2 = 0.3
    loop = 100
    task_size = 10
    reality = Reality(m=m, s=s)
    # individual = Individual(m=m, p1=p1, reality=reality)
    organization = Organization(m=m, s=s, n=n, p1=p1, p2=p2, reality=reality)
    organization.process(loop=loop, task_size=task_size)
    x = range(loop)
    plt.plot(x, organization.performance_curve, "k-")
    # plt.savefig("search.jpg")
    plt.title('Search Evolution')
    plt.xlabel('Time')
    plt.ylabel('Performance')
    # plt.legend()
    plt.show()
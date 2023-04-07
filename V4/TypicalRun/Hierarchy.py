# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Hierarchy.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual import Individual
import numpy as np
import math
from Reality import Reality
from Superior import Superior
from Team import Team
import time
import pickle


class Hierarchy:
    def __init__(self, m=None, s=None, n=None, reality=None, lr=None, alpha=3,
                 group_size=None, p1=0.1, p2=0.9, manager_num=50, confirmation=True):
        """
        :param m: problem space
        :param s: the first complexity
        :param t: the second complexity
        :param n: the number of agents
        :param reality: to provide feedback
        """
        self.m = m  # state length
        self.s = s  # lower-level interdependency
        self.n = n
        self.manager_num = manager_num
        self.group_size = group_size
        self.confirmation = confirmation  # whether or the lower-level individual initially confirm to the upper-level
        if self.m % self.s != 0:
            raise ValueError("m is not dividable by s")
        if self.manager_num * self.group_size != self.n:
            print("auto-adjust the unfit manager_num")
            self.manager_num = self.n // self.group_size
        self.alpha = alpha
        self.policy_num = self.m // self.alpha
        self.lr = lr  # learning rate
        self.reality = reality
        manager_num = self.n // self.group_size
        self.superior = Superior(policy_num=self.policy_num, reality=self.reality, manager_num=manager_num, p1=p1, p2=p2)
        # n is the number of managers, instead of employers;  In March's paper, n=50
        # p1, p2 is set to be the best one in March's paper
        self.teams = []
        for i in range(self.n // self.group_size):
            team = Team(m=self.m, index=i, alpha=self.alpha, reality=self.reality)
            for _ in range(self.group_size):
                individual = Individual(m=self.m, s=self.s, alpha=self.alpha, reality=self.reality, lr=self.lr)
                team.individuals.append(individual)
            team.manager = self.superior.managers[i]
            if self.confirmation:
                team.confirm(policy=team.manager.policy)
            self.teams.append(team)
        # DVs
        # self.performance_across_time = []
        # self.variance_across_time = []
        # self.diversity_across_time = []
        # self.superior_performance_across_time = []

    def search(self):
        # Supervision Formation
        self.superior.search()
        # Autonomous team learning
        for team in self.teams:
            team.confirm(policy=team.manager.policy)
            team.form_individual_majority_view()
            team.learn()
        # performance_list = []
        # for team in self.teams:
        #     performance_list += [individual.payoff for individual in team.individuals]
        # self.performance_across_time.append(sum(performance_list) / len(performance_list))
        # self.variance_across_time.append(np.std(performance_list))
        # self.diversity_across_time.append(self.get_diversity())

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
    t0 = time.time()
    m = 90
    s = 1
    n = 1225  # 50 managers, each manager control one autonomous team; 50*7=350
    lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    p1 = 0.1  # belief learning from code
    p2 = 0.9  # code learning from belief
    search_iteration = 500
    reality = Reality(m=m, s=s)
    hierarchy = Hierarchy(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size, p1=p1, p2=p2)
    individual_performance_list = []
    for _ in range(search_iteration):
        individual_performance = []
        for team in hierarchy.teams:
            individual_performance += [individual.payoff for individual in team.individuals]
        individual_performance_list.append(individual_performance)
        hierarchy.search()

    with open("hierarchy_typical_run", 'wb') as out_file:
        pickle.dump(individual_performance_list, out_file)
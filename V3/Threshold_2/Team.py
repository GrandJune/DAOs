# -*- coding: utf-8 -*-
# @Time     : 2/1/2023 10:48
# @Author   : Junyi
# @FileName: Team.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import math
from Individual import Individual
from Reality import Reality
import numpy as np

class Team:
    def __init__(self, m=None, index=None, alpha=None, reality=None):
        self.index = index
        self.m = m
        self.alpha = alpha
        self.policy_num = self.m // self.alpha
        self.individuals = []
        self.manager = None
        self.reality = reality
        self.policy = [0] * self.policy_num
        self.belief = [0] * self.m
        self.token = None

    def form_team_policy(self, token=False):
        for individual in self.individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)
        if token:
            for i in range(self.policy_num):
                tendency = sum([individual.policy[i] * individual.token for individual in self.individuals])
                if tendency > 0:
                    self.policy[i] = 1
                elif tendency < 0:
                    self.policy[i] = -1
                else:
                    self.policy[i] = 0
        else:
            for i in range(self.policy_num):
                tendency = sum([individual.policy[i] for individual in self.individuals])
                if tendency > 0:
                    self.policy[i] = 1
                elif tendency < 0:
                    self.policy[i] = -1
                else:
                    self.policy[i] = 0

    def form_team_belief(self, token=False):
        if token:
            for i in range(self.m):
                tendency = sum([individual.belief[i] * individual.token for individual in self.individuals])
                if tendency > 0:
                    self.belief[i] = 1
                elif tendency < 0:
                    self.belief[i] = -1
                else:
                    self.belief[i] = 0
        else:
            for i in range(self.m):
                tendency = sum([individual.belief[i] for individual in self.individuals])
                if tendency > 0:
                    self.belief[i] = 1
                elif tendency < 0:
                    self.belief[i] = -1
                else:
                    self.belief[i] = 0

    def update_token(self,):
        self.token = sum([individual.token for individual in self.individuals])

    def form_individual_majority_view(self):
        for individual in self.individuals:
            superior_belief_pool = [other.belief for other in self.individuals
                                    if other.payoff > individual.payoff]
            if len(superior_belief_pool) == 0:  # only those have better reference will learn / update their belief
                individual.superior_majority_view = None
            else:
                majority_view = []
                for i in range(self.m):
                    temp = [belief[i] for belief in superior_belief_pool]
                    if sum(temp) > 0:
                        majority_view.append(1)
                    elif sum(temp) < 0:
                        majority_view.append(-1)
                    else:
                        majority_view.append(0)
                individual.superior_majority_view = majority_view

    def adjust_majority_view_2_consensus(self, policy=None):
        for individual in self.individuals:
            if not individual.superior_majority_view:
                continue
            for index in range(self.policy_num):
                if (policy[index] == 0) and (np.random.uniform(0, 1) < (1 - individual.lr)):
                    # if do nothing in case of zero, cannot enable sufficient search
                    # using learning rate \eta: would like to adopt the others' perception
                    # Thus with a probability of (1- \eta) to retain the previous belief
                    continue
                else:
                    if sum(individual.superior_majority_view
                           [index * self.alpha: (index + 1) * self.alpha]) != policy[index]:
                        individual.superior_majority_view[index * self.alpha: (index + 1) * self.alpha] = \
                            self.reality.policy_2_belief(policy=policy[index])

    def confirm(self, policy=None):
        # individual first confirm to the consensus
        for individual in self.individuals:
            for index in range(self.policy_num):
                if policy[index] == 0:
                    continue
                else:
                    if sum(individual.belief[index * self.alpha: (index + 1) * self.alpha]) != policy[index]:
                        individual.belief[index * self.alpha: (index + 1) * self.alpha] = self.reality.policy_2_belief(
                            policy=policy[index])

    def learn(self):
        for individual in self.individuals:
            individual.learning_from_belief(belief=individual.superior_majority_view)

if __name__ == '__main__':
    # test
    m = 30
    s = 1
    n = 10
    lr = 0.3
    auto_lr = 0.5
    loop = 100
    version = "Rushed"
    reality = Reality(m=m, s=s, version=version)
    from DAO import Team
    for _ in range(n):
        individual = Individual(m=m, s=s, reality=reality, lr=lr)
        team.individuals.append(individual)
    for individual in team.individuals:
        print(individual.belief, individual.payoff)
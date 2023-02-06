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
    def __init__(self, m=None, index=None, policy_num=None, reality=None):
        self.index = index
        self.m = m
        self.policy_num = policy_num
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

    def confirm(self, policy=None):
        # individual first confirm to the consensus
        for individual in self.individuals:
            for index in range(self.policy_num):
                if policy[index] == 0:
                    continue
                else:
                    if sum(individual.belief[index * 3: (index + 1) * 3]) != policy[index]:
                        individual.belief[index * 3: (index + 1) * 3] = self.reality.policy_2_belief(
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
    team = Team(policy_num=m // 3)
    for _ in range(n):
        individual = Individual(m=m, s=s, reality=reality, lr=lr)
        team.individuals.append(individual)
    for individual in team.individuals:
        print(individual.belief, individual.payoff)
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

    def form_individual_majority_view(self):
        for individual in self.individuals:
            superior_belief_pool = [other.belief for other in self.individuals
                                    if other.payoff > individual.payoff]
            if len(superior_belief_pool) == 0:
                individual.superior_majority_view = None
            else:
                majority_view = []
                for i in range(self.m):
                    temp = [belief[i] for belief in superior_belief_pool]
                    if sum(temp) > 0:
                        majority_view.append(1)
                    elif sum(temp) < 0:
                        majority_view.append(-1)
                    else:  # when there is no inclination as reference, agents will become uncertain
                        majority_view.append(0)
                individual.superior_majority_view = majority_view

    def adjust_majority_view_2_consensus(self, policy=None):
        for individual in self.individuals:
            # If IS the best one
            if individual.superior_majority_view == None:
                individual.superior_majority_view = individual.belief.copy()
                for index in range(self.policy_num):
                    # if the consensus is zero, agents will learn from chaos (exploration)
                    individual.superior_majority_view[index * self.alpha: (index + 1) * self.alpha] = \
                        self.reality.policy_2_belief(policy=policy[index])
            else:  # NOT the best one
                for index in range(self.policy_num):
                    # if the consensus is zero, agents will learn from chaos (exploration)
                    if sum(individual.superior_majority_view
                           [index * self.alpha: (index + 1) * self.alpha]) != policy[index]:
                        individual.superior_majority_view[index * self.alpha: (index + 1) * self.alpha] = \
                            self.reality.policy_2_belief(policy=policy[index])

    def confirm(self, policy=None):
        # individual first confirm to the supervision
        for individual in self.individuals:
            for index in range(self.policy_num):
                # if the supervision is zero, will retain the previous belief (lazy employee)
                if policy[index] == 0:
                    continue
                else:
                    if sum(individual.belief[index * self.alpha: (index + 1) * self.alpha]) != policy[index]:
                        individual.belief[index * self.alpha: (index + 1) * self.alpha] = self.reality.policy_2_belief(
                            policy=policy[index])
            individual.payoff = self.reality.get_payoff(belief=individual.belief)
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)

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

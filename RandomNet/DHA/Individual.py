# -*- coding: utf-8 -*-
# @Time     : 24/01/2024 19:05
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import time
import numpy as np
from Reality import Reality


class Individual:
    def __init__(self, m=None, reality=None, lr=None, alpha=3):
        self.m = m
        self.alpha = alpha
        self.policy_num = self.m // self.alpha
        self.lr = lr  # learning rate, learning from (adjusted) majority view
        self.token = None  # should introduce more dimensions of token
        self.connections = []  # id for learning reference
        self.reality = reality
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        # self.belief = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)  # a fake policy for voting
        self.superior_majority_view = []

    def learning_from_belief(self, belief=None):
        if len(belief) != self.m:
            raise ValueError("Belief length {0} is not equal to {1}".format(len(belief), self.m))
        for i in range(self.m):
            if belief[i] == 0:
                continue
            elif belief[i] != self.belief[i]:
                if np.random.uniform(0, 1) < self.lr:
                    self.belief[i] = belief[i]
            else:
                pass  # retain the previous belief
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)

    def form_superior_majority_view(self, superior_belief_pool=None):
        if len(superior_belief_pool) == 0:
            # The best performing actors will not learn from peers
            self.superior_majority_view = []
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
            self.superior_majority_view = majority_view

    def adjust_majority_view_2_consensus(self, consensus=None):
        if len(self.superior_majority_view) == 0:
            return
        for index in range(self.policy_num):
            # if the consensus is zero, agents will learn from chaos
            if sum(self.superior_majority_view
                   [index * self.alpha: (index + 1) * self.alpha]) != consensus[index]:
                self.superior_majority_view[index * self.alpha: (index + 1) * self.alpha] = \
                    self.reality.policy_2_belief(policy=consensus[index])

    def adjust_belief_2_supervision(self, policy=None):
        for index in range(self.policy_num):
            # if the supervision is zero, will retain the previous belief (lazy employee)
            if policy[index] == 0:
                continue
            else:
                if sum(self.belief[index * self.alpha: (index + 1) * self.alpha]) != policy[index]:
                    self.belief[index * self.alpha: (index + 1) * self.alpha] = self.reality.policy_2_belief(policy=policy[index])
        individual.payoff = self.reality.get_payoff(belief=individual.belief)
        individual.policy = self.reality.belief_2_policy(belief=individual.belief)

    def turnover(self, turnover_rate=None):
        for index in range(self.m):
            if np.random.uniform(0, 1) < turnover_rate:
                self.belief[index] *= -1
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        self.superior_majority_view = None


if __name__ == '__main__':
    m = 30
    s = 1
    n = 10
    lr = 0.3
    version = "Rushed"
    loop = 100
    reality = Reality(m=m, version=version)
    team = []
    for _ in range(n):
        individual = Individual(m=m, reality=reality, lr=lr)
        team.append(individual)
    consensus = reality.real_policy
    performance_across_time = []
    policy_performance_across_time = []
    # for _ in range(loop):
    #     for individual in team:
    #         individual.superior_payoff = max([individual.payoff for individual in team])
    #     for individual in team:
    #         individual.learning_from_belief(policy=consensus)
    #     # print(team.individuals[0].policy_)
    #     policy_payoff_list = [individual.policy_payoff for individual in team.individuals]
    #     payoff_list = [individual.payoff for individual in team.individuals]
    #     policy_performance_across_time.append(sum(policy_payoff_list) / len(policy_payoff_list))
    #     performance_across_time.append(sum(payoff_list) / len(payoff_list))
    # import matplotlib.pyplot as plt
    # x = range(loop)
    # plt.plot(x, performance_across_time, "r-", label="Belief")
    # plt.plot(x, policy_performance_across_time, "b-", label="Policy")
    # # plt.title('Diversity Decrease')
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Performance', fontweight='bold', fontsize=10)
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_performance.png", transparent=True, dpi=1200)
    # plt.show()
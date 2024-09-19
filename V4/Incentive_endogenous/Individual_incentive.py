# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 19:53
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import time
import numpy as np
from Reality import Reality


class Individual:
    def __init__(self, m=None, reality=None, lr=None, alpha=3, sensitivity=None):
        self.m = m
        self.alpha = alpha # integration
        self.policy_num = self.m // self.alpha
        self.lr = lr  # learning rate, learning from (adjusted) majority view
        self.token = None  # should introduce more dimensions of token
        self.active = 1  # For the incentive search
        self.sensitivity = sensitivity  # apply an exponential scaling to the wealth.
        # a factor controls how strongly the probability increases with wealth.
        self.reality = reality
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        # self.belief = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)  # a fake policy for voting
        self.superior_majority_view = None

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

    def experimentation(self, experimentation_rate=None):
        for index in range(self.m):
            if np.random.uniform(0, 1) < experimentation_rate:
                self.belief[index] *= -1
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        self.superior_majority_view = None

    def turnover(self, turnover_rate=None):
        if np.random.uniform(0, 1) < turnover_rate:
            self.belief = np.random.choice([-1, 0, 1], self.m, p=[1 / 3, 1 / 3, 1 / 3])
            self.payoff = self.reality.get_payoff(belief=self.belief)
            self.policy = self.reality.belief_2_policy(belief=self.belief)
            self.superior_majority_view = None


if __name__ == '__main__':
    from Team import Team
    m = 60
    n = 7
    lr = 0.3
    search_loop = 100
    reality = Reality(m=m)
    team = Team(m=m, index=None, alpha=3, reality=reality)
    for _ in range(n):
        individual = Individual(m=m, reality=reality, lr=lr)
        team.individuals.append(individual)
    consensus = reality.real_policy
    performance_across_time = []
    for _ in range(search_loop):
        team.form_individual_majority_view()
        team.learn()
        performance_list = [individual.payoff for individual in team.individuals]
        performance_across_time.append(sum(performance_list) / len(performance_list))
    import matplotlib.pyplot as plt
    x = range(search_loop)
    plt.plot(x, performance_across_time, "r-", label="Belief")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("DAO_performance.png", transparent=True, dpi=1200)
    plt.show()
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
    def __init__(self, m=None, s=None, reality=None, lr=None, alpha=3):
        self.m = m
        self.s = s
        self.alpha = alpha
        self.policy_num = self.m // self.alpha
        self.lr = lr  # learning rate, learning from (adjusted) majority view
        self.token = None  # should introduce more dimensions of token
        self.active = True  # whether the agent is active in voting/learning

        self.reality = reality
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        # self.belief = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)  # a fake policy for voting
        self.superior_majority_view = None

    def learning_from_belief(self, belief=None):
        if not belief:
            return
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

    def turnover(self):
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
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
    reality = Reality(m=m, s=s, version=version)
    team = []
    for _ in range(n):
        individual = Individual(m=m, s=s, reality=reality, lr=lr)
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
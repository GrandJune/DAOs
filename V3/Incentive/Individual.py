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
    def __init__(self, m=None, s=None, reality=None, lr=None):
        self.m = m
        self.s = s
        self.lr = lr  # learning rate, learning from (adjusted) majority view
        self.token = None  # should introduce more dimensions of token
        self.connections = []  # for autonomy, to seek for superior subgroup
        self.group_id = None
        self.reality = reality
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        # self.belief = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy_num = self.m // 3
        self.policy = self.reality.belief_2_policy(belief=self.belief)  # a fake policy for voting
        # self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)
        self.superior_majority_view = None

    def learning_from_belief(self, belief=None):
        if len(belief) != self.m:
            raise ValueError("Learning from a wrong belief (not autonomous majority view)")
        for i in range(self.m):
            if belief[i] != 0:
                if np.random.uniform(0, 1) < self.lr:
                    self.belief[i] = belief[i]
            else:
                pass  # retain the previous belief
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        # self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

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
    auto_lr = 0.5
    version = "Rushed"
    loop = 100
    reality = Reality(m=m, s=s, version=version)
    from DAO import Team
    team = Team(policy_num=m // 3)
    for _ in range(n):
        individual = Individual(m=m, s=s, reality=reality, lr=lr)
        team.individuals.append(individual)
    consensus = reality.real_policy
    performance_across_time = []
    policy_performance_across_time = []
    for _ in range(loop):
        for individual in team.individuals:
            individual.superior_payoff = max([individual.payoff for individual in team.individuals])
        for individual in team.individuals:
            individual.learning_from_policy(policy=consensus)
        # print(team.individuals[0].policy_)
        policy_payoff_list = [individual.policy_payoff for individual in team.individuals]
        payoff_list = [individual.payoff for individual in team.individuals]
        policy_performance_across_time.append(sum(policy_payoff_list) / len(policy_payoff_list))
        performance_across_time.append(sum(payoff_list) / len(payoff_list))
    import matplotlib.pyplot as plt
    x = range(loop)
    plt.plot(x, performance_across_time, "r-", label="Belief")
    plt.plot(x, policy_performance_across_time, "b-", label="Policy")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("DAO_performance.png", transparent=True, dpi=1200)
    plt.show()


    # only use belief, avoid policy-belief transformation
    # performance_across_time = []
    # for _ in range(loop):
    #     belief_pool = [individual.belief for individual in team.individuals]
    #     majority_view = reality.get_majority_view(superior_belief=belief_pool)
    #     for individual in team.individuals:
    #         individual.learning_from_belief(belief=majority_view)
    #     payoff_list = [individual.payoff for individual in team.individuals]
    #     # policy_performance_across_time.append(sum(policy_payoff_list) / len(policy_payoff_list))
    #     performance_across_time.append(sum(payoff_list) / len(payoff_list))
    # import matplotlib.pyplot as plt
    # x = range(loop)
    # plt.plot(x, performance_across_time, "r-", label="Belief")
    # # plt.plot(x, policy_performance_across_time, "b-", label="Policy")
    # # plt.title('Diversity Decrease')
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Performance', fontweight='bold', fontsize=10)
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_performance.png", transparent=True, dpi=1200)
    # plt.show()

# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import math
from Individual import Individual
from Team import Team
from Reality import Reality
import numpy as np


class DAO:
    def __init__(self, m=None, s=None, n=None, reality=None, lr=None, group_size=None):
        """
        :param m: problem space
        :param s: the first complexity
        :param n: the number of agents
        :param reality: to provide feedback
        """
        self.m = m  # state length
        self.s = s  # lower-level interdependency
        self.n = n  # the number of subunits under this superior
        if self.m % self.s != 0:
            raise ValueError("m is not dividable by s")
        if self.m % 3 != 0:
            raise ValueError("m is not dividable by 3")
        self.policy_num = self.m // 3
        self.reality = reality
        self.lr = lr  # learning from consensus
        self.group_size = group_size
        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.teams = []
        for i in range(self.n // self.group_size):
            team = Team(m=self.m, index=i, policy_num=self.policy_num, reality=self.reality)
            for _ in range(self.group_size):
                individual = Individual(m=self.m, s=self.s, reality=self.reality, lr=self.lr)
                team.individuals.append(individual)
            team.get_policy(token=False)
            self.teams.append(team)
        self.performance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []

    def search(self, threshold_ratio=None, token=False):
        # Consensus Formation
        new_consensus = []
        if not token:
            threshold = threshold_ratio * (self.n // self.group_size)
            for team in self.teams:
                team.get_policy(token=False)
            for i in range(self.policy_num):
                policy_list = [team.policy[i] for team in self.teams]
                positive_count = sum([1 for each in policy_list if each == 1])
                negative_count = sum([1 for each in policy_list if each == -1])
                if (positive_count > threshold) and sum(policy_list) > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and sum(policy_list) < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)

        else:  # With token
            for team in self.teams:
                team.update_token()
                team.get_policy(token=False)  # within the teams, still use simple majority
            threshold = threshold_ratio * sum([team.token for team in self.teams])
            for i in range(self.policy_num):
                policy_sum = sum([team.policy[i] for team in self.teams])
                positive_count = sum([team.token for team in self.teams if team.policy[i] == 1])
                negative_count = sum([team.token for team in self.teams if team.policy[i] == -1])
                if (positive_count > threshold) and policy_sum > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and policy_sum < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)
        self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)
        # 1) Generate and 2) adjust the superior majority view and then 3) learn from it
        for team in self.teams:
            team.get_majority_view()
            team.follow_consensus(consensus=new_consensus)
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

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
                    if np.random.uniform(0, 1) < turnover_rate:
                        individual.turnover()


if __name__ == '__main__':
    m = 60
    s = 1
    n = 350
    search_loop = 200
    lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, s=s, version="Rushed")
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size)
    # dao.teams[0].individuals[0].belief = reality.real_code.copy()
    # dao.teams[0].individuals[0].payoff = reality.get_payoff(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].payoff)
    for _ in range(search_loop):
        dao.search(threshold_ratio=0.6)
        print(dao.consensus)
        # print(dao.teams[0].individuals[0].belief, dao.teams[0].individuals[0].payoff)
    import matplotlib.pyplot as plt
    x = range(search_loop)
    plt.plot(x, dao.performance_across_time, "r-", label="DAO")
    plt.plot(x, dao.consensus_performance_across_time, "b-", label="Consensus")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_performance.png", transparent=True, dpi=1200)
    plt.show()



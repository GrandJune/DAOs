# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual import Individual
from Reality import Reality
import numpy as np


class DAO:
    def __init__(self, m=None, s=None, n=None, reality=None, lr=None, auto_lr=None, subgroup_size=None):
        """
        :param m: problem space
        :param s: the first complexity
        :param n: the number of agents
        :param reality: to provide feedback
        :param confirm: the extent to which agents confirm to their superior
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
        self.auto_lr = auto_lr  # autonomous learning
        self.subgroup_size = subgroup_size
        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.teams = []
        team = Team(policy_num=self.policy_num)
        for i in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=self.reality, lr=self.lr, auto_lr=self.auto_lr)
            team.individuals.append(individual)
            if (i + 1) % self.subgroup_size == 0:
                self.teams.append(team)
                team = Team(policy_num=self.policy_num)
        self.performance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []

    def search(self):
        # For DAO, we integrate the autonomous team together, and each of these autonomous teams are based on Fang's model
        # first make the autonomous team converge
        for _ in range(20):
            for team in self.teams:
                for individual in team.individuals:
                    superior_belief = [i.belief for i in team.individuals if i.payoff > individual.payoff]
                    majority_view = self.get_majority_view(superior_belief=superior_belief)
                    individual.learning_from_belief(belief=majority_view)
        for team in self.teams:
            team.form_policy()
        new_consensus = []
        for i in range(self.policy_num):
            temp = sum([team.policy[i] for team in self.teams])
            if temp > 0:
                new_consensus.append(1)
            elif temp < 0:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)
        self.consensus = new_consensus.copy()
        self.consensus_payoff = self.reality.get_policy_payoff(policy=self.consensus)
        for team in self.teams:
            for individual in team.individuals:
                # if self.consensus_payoff > individual.policy_payoff:
                individual.learning_from_policy(policy=self.consensus)  # using lr
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        # self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

    def get_majority_view(self, superior_belief=None):
        majority_view = []
        for i in range(self.m):
            temp = [belief[i] for belief in superior_belief]
            if sum(temp) > 0:
                majority_view.append(1)
            elif sum(temp) < 0:
                majority_view.append(-1)
            else:
                majority_view.append(0)
        return majority_view

    def get_diversity(self):
        belief_pool = [individual.belief for individual in self.individuals]
        diversity = 0
        for index, individual in enumerate(self.individuals):
            selected_pool = belief_pool[index+1::]
            one_pair_diversity = [self.get_distance(individual.belief, belief) for belief in selected_pool]
            diversity += sum(one_pair_diversity)
        return diversity / self.m / (self.n - 1) / self.n * 2

    def get_distance(self, a=None, b=None):
        acc = 0
        for i in range(self.m):
            if a[i] != b[i]:
                acc += 1
        return acc


class Team:
    def __init__(self, policy_num=None):
        self.individuals = []
        self.policy = []
        self.policy_num = policy_num

    def form_policy(self):
        policy = []
        for i in range(self.policy_num):
            temp = [individual.policy[i] for individual in self.individuals]
            if sum(temp) > 0:
                policy.append(1)
            elif sum(temp) < 0:
                policy.append(-1)
            else:
                policy.append(0)
        self.policy = policy



if __name__ == '__main__':
    m = 30
    s = 1
    n = 200
    lr = 0.9
    auto_lr = 0.5
    group_size = 10  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size, auto_lr=auto_lr)
    for _ in range(20):
        dao.search()
    import matplotlib.pyplot as plt
    x = range(20)
    plt.plot(x, dao.performance_across_time, "r-", label="DAO")
    plt.plot(x, dao.consensus_performance_across_time, "b-", label="Consensus")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_performance.png", transparent=True, dpi=1200)
    plt.show()

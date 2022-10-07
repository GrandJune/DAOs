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
        self.individuals = []
        # team = Team(policy_num=self.policy_num)
        for i in range(self.n):
            individual = Individual(m=self.m, s=self.s, reality=self.reality, auto_lr=self.auto_lr, lr=self.lr)
            individual.connections = list(range((i // self.subgroup_size) * self.subgroup_size, ((i // self.subgroup_size) + 1) * self.subgroup_size))
            self.individuals.append(individual)
        self.performance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []

    def search(self):
        # Consensus Formation
        new_consensus = []
        threshold = 0
        for i in range(self.policy_num):
            temp = sum([individual.policy[i] for individual in self.individuals])
            if temp > threshold:
                new_consensus.append(1)
            elif temp < -threshold:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)
        self.consensus = new_consensus.copy()
        self.consensus_payoff = self.reality.get_policy_payoff(policy=self.consensus)
        # Adjust the superior majority view and then learn from it
        for individual in self.individuals:
            connected_group = [self.individuals[i] for i in individual.connections]
            superior_belief_pool = []
            for each in connected_group:
                if each.payoff > individual.payoff:
                    superior_belief_pool.append(each.belief)
            if len(superior_belief_pool) != 0:
                majority_view = self.get_majority_view(superior_belief_pool)
                individual.superior_majority_view = majority_view
            else:
                individual.superior_majority_view = None

        for individual in self.individuals:
            if individual.superior_majority_view:  # only those have better reference will learn / update their belief
                individual.superior_majority_view = \
                    self.adjust_majority_view(majority_view=individual.superior_majority_view)
                for index in range(self.m):
                    if np.random.uniform(0, 1) < individual.lr:
                        individual.belief[index] = individual.superior_majority_view[index]
            individual.payoff = self.reality.get_payoff(belief=individual.belief)
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)
            individual.policy_payoff = self.reality.get_policy_payoff(policy=individual.policy)

        performance_list = [individual.payoff for individual in self.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        # self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

    def get_majority_view(self, belief_pool=None):
        majority_view = []
        for i in range(self.m):
            temp = [belief[i] for belief in belief_pool]
            if sum(temp) > 0:
                majority_view.append(1)
            elif sum(temp) < 0:
                majority_view.append(-1)
            else:
                majority_view.append(0)
        return majority_view

    def get_diversity(self):
        individual_pool = []
        for team in self.teams:
            individual_pool += team.individuals
        diversity = 0
        belief_pool = [individual.belief for individual in individual_pool]
        for index, individual in enumerate(individual_pool):
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

    def adjust_majority_view(self, majority_view=None):
        adjusted_majority_view = majority_view.copy()
        if len(adjusted_majority_view) != self.m:
            raise ValueError("The length of majority view should be m")
        for index in range(self.policy_num):
            if sum(adjusted_majority_view[index*3: (index+1)*3]) != self.consensus[index]:
                adjusted_majority_view[index * 3: (index + 1) * 3] = self.reality.policy_2_belief(policy=self.consensus[index])
        return adjusted_majority_view


if __name__ == '__main__':
    m = 30
    s = 1
    n = 140
    lr = 0.3
    auto_lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size, auto_lr=auto_lr)
    # dao.teams[0].individuals[0].belief = reality.real_code.copy()
    # dao.teams[0].individuals[0].payoff = reality.get_payoff(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].payoff)
    for _ in range(100):
        dao.search()
        # print(dao.teams[0].individuals[0].belief, dao.teams[0].individuals[0].payoff)
    import matplotlib.pyplot as plt
    x = range(100)
    plt.plot(x, dao.performance_across_time, "r-", label="DAO")
    plt.plot(x, dao.consensus_performance_across_time, "b-", label="Consensus")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_performance.png", transparent=True, dpi=1200)
    plt.show()
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
            individual = Individual(m=self.m, s=self.s, reality=self.reality, lr=self.lr, auto_lr=self.auto_lr)
            self.individuals.append(individual)
        for i in range(self.n // self.subgroup_size):
            team = Team(policy_num=self.policy_num)
            team.individuals = self.individuals[i*self.subgroup_size:(i+1)*self.subgroup_size]
            self.teams.append(team)
        self.performance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []

    def search(self):
        # Consensus learning
        new_consensus = []
        individual_pool = []
        for team in self.teams:
            individual_pool += team.individuals
            payoff_list = [individual.payoff for individual in team.individuals]
            team.gap = max(payoff_list) - min(payoff_list)
            # print("Gap: ", team.gap)
        thredhold = 1/3 * self.n
        # thredhold = 0.05 * self.n
        for i in range(self.policy_num):
            temp = sum([individual.policy[i] for individual in individual_pool])
            if temp > thredhold:
                new_consensus.append(1)
            elif temp < -thredhold:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)
        self.consensus = new_consensus.copy()
        self.consensus_payoff = self.reality.get_policy_payoff(policy=self.consensus)
        # print("consensus: ", self.consensus, self.consensus_payoff)
        # Autonomous learning
        for team in self.teams:
            for individual in team.individuals:
                superior_belief_pool = [i.belief for i in team.individuals if i.payoff > individual.payoff]
                if len(superior_belief_pool) == 0:
                    majority_belief = individual.belief
                else:
                    majority_belief = self.get_majority_view(belief_pool=superior_belief_pool)
                majority_policy = self.reality.belief_2_policy(belief=majority_belief)
                for i in range(self.policy_num):
                    if majority_policy[i] * self.consensus[i] == -1:
                        majority_belief[i * 3: (i + 1) * 3] = self.reality.policy_2_belief(policy=self.consensus[i])
                for j in range(self.m):
                    if np.random.uniform(0,1) < individual.lr:
                        individual.belief[j] = majority_belief[j]
                individual.payoff = self.reality.get_payoff(belief=individual.belief)
                individual.policy = self.reality.belief_2_policy(belief=individual.belief)
                individual.policy_payoff = self.reality.get_policy_payoff(policy=individual.policy)

        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]
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



if __name__ == '__main__':
    m = 30
    s = 1
    n = 1000
    lr = 0.3
    auto_lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size, auto_lr=auto_lr)
    # dao.teams[0].individuals[0].belief = reality.real_code.copy()
    # dao.teams[0].individuals[0].payoff = reality.get_payoff(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].payoff)
    for _ in range(50):
        dao.search()
        max_list =[]
        for team in dao.teams:
            max_  = max([individual.payoff for individual in dao.teams[0].individuals])
            max_list.append(max_)
        print(max_list)
        # print(dao.teams[0].individuals[0].belief, dao.teams[0].individuals[0].payoff)
    import matplotlib.pyplot as plt
    x = range(50)
    plt.plot(x, dao.performance_across_time, "r-", label="DAO")
    plt.plot(x, dao.consensus_performance_across_time, "b-", label="Consensus")
    # plt.title('Diversity Decrease')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_performance.png", transparent=True, dpi=1200)
    plt.show()

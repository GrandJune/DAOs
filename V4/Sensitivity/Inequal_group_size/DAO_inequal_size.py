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
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size_list=None,
                 alpha=3):
        """
        :param m: problem space
        :param n: the number of agents
        :param reality: to provide feedback
        """
        self.m = m  # state length
        # self.n = n  # the number of subunits under this superior
        if self.m % alpha != 0:
            raise ValueError("m is not dividable by {0}".format(alpha))
        self.alpha = alpha  # The aggregation degree
        self.policy_num = self.m // self.alpha
        self.reality = reality
        self.lr = lr  # learning from consensus
        # self.group_size = group_size
        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.teams = []
        # Inequal Group Size (some are 7, and some are 14, etc)
        for group_size in group_size_list:
            team = Team(m=self.m, alpha=self.alpha, reality=self.reality)
            for _ in range(group_size):
                individual = Individual(m=self.m, alpha=self.alpha, reality=self.reality, lr=self.lr)
                team.individuals.append(individual)
            self.teams.append(team)
        self.n = sum(group_size_list)
        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []

    def search(self, threshold_ratio=None, token=False):
        # Consensus Formation
        new_consensus = []
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)

        if not token:
            threshold = threshold_ratio * self.n
            for i in range(self.policy_num):
                crowd_opinion = [individual.policy[i] for individual in individuals]
                positive_count = sum([1 for each in crowd_opinion if each == 1])
                negative_count = sum([1 for each in crowd_opinion if each == -1])
                if (positive_count > threshold) and sum(crowd_opinion) > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and sum(crowd_opinion) < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)

        else:  # With token
            threshold = threshold_ratio * sum([individual.token for individual in individuals])
            for i in range(self.policy_num):
                overall_sum = sum([individual.policy[i] * individual.token for individual in individuals])
                positive_count = sum([individual.token for individual in individuals if individual.policy[i] == 1])
                negative_count = sum([individual.token for individual in individuals if individual.policy[i] == -1])
                if (positive_count > threshold) and overall_sum > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and overall_sum < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)
        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)
        # 1) Generate and 2) adjust the superior majority view and then 3) learn from it
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]

        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

    def incentive_search(self, threshold_ratio=None, incentive=1, inactive_rate=None):
        new_consensus = []
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)
        for individual in individuals:
            if np.random.uniform(0, 1) < inactive_rate:  # if inactive, e.g., 0.2
                if np.random.uniform(0, 1) < incentive:   # if incentivized, e.g., 0.8
                    individual.active = 1
                else:
                    individual.active = 0
            else:
                individual.active = 1
        threshold = threshold_ratio * sum([individual.token for individual in individuals])
        # consider the active status
        for i in range(self.policy_num):
            overall_sum = sum([individual.policy[i] * individual.token * individual.active for individual in individuals])
            positive_count = sum([individual.token for individual in individuals if (individual.policy[i] == 1) and (individual.active == 1)])
            negative_count = sum([individual.token for individual in individuals if (individual.policy[i] == -1) and (individual.active == 1)])
            if (positive_count > threshold) and overall_sum > 0:
                new_consensus.append(1)
            elif (negative_count > threshold) and overall_sum < 0:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)
        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)
        # 1) Generate and 2) adjust the superior majority view and 3) learn from it
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]

        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
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

    def get_gini(self):
        array = []
        for team in self.teams:
            for individual in team.individuals:
                array.append(individual.token)
        array = sorted(array)
        n = len(array)
        coefficient = 0
        for i, value in enumerate(array):
            coefficient += (2 * i - n) * value
        coefficient /= n * sum(array)
        return coefficient

    def turnover(self, turnover_rate=None):
        if turnover_rate:
            for team in self.teams:
                for individual in team.individuals:
                    individual.turnover(turnover_rate=turnover_rate)

    def experimentation(self, experimentation_rate=None):
        if experimentation_rate:
            for team in self.teams:
                for individual in team.individuals:
                    individual.experimentation(experimentation_rate=experimentation_rate)


if __name__ == '__main__':
    m = 60
    n = 280
    search_loop = 100
    lr = 0.3
    alpha = 3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, version="Rushed", alpha=3)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, alpha=3)
    # dao.teams[0].individuals[0].belief = reality.real_code.copy()
    # dao.teams[0].individuals[0].payoff = reality.get_payoff(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].payoff)
    for period in range(search_loop):
        dao.incentive_search(threshold_ratio=0.5, incentive=50)
        # print(period, dao.consensus, reality.real_policy, reality.real_code)
        # print(dao.teams[0].individuals[0].belief, dao.teams[0].individuals[0].policy,
        #       dao.teams[0].individuals[0].payoff)
        print("--{0}--".format(period))
    import matplotlib.pyplot as plt
    x = range(search_loop)

    plt.plot(x, dao.performance_across_time, "k-", label="Mean")
    plt.plot(x, dao.consensus_performance_across_time, "r-", label="Consensus")
    plt.title('Performance')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("DAO_performance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Diversity
    plt.plot(x, dao.diversity_across_time, "k-", label="DAO")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    plt.title('Diversity')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("DAO_diversity.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Variance
    plt.plot(x, dao.variance_across_time, "k-", label="DAO")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("DAO_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # # Gini Index
    # plt.plot(x, dao.gini_across_time, "k-", label="DAO")
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Gini Index', fontweight='bold', fontsize=10)
    # plt.title('Gini Index')
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_gini.png", transparent=False, dpi=1200)
    # plt.show()
    # plt.clf()

    # Reward number
    # plt.plot(x, dao.reward_num_across_time, "k-", label="DAO")
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Reward Number', fontweight='bold', fontsize=10)
    # plt.title('Reward Number')
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_gini.png", transparent=False, dpi=1200)
    # plt.show()
    # plt.clf()



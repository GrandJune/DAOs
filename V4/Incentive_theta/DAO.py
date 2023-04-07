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
    def __init__(self, m=None, s=None, n=None, reality=None, lr=None, group_size=None,
                 alpha=3):
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
        if self.m % alpha != 0:
            raise ValueError("m is not dividable by {0}".format(alpha))
        self.alpha = alpha  # The aggregation degree
        self.policy_num = self.m // self.alpha
        self.reality = reality
        self.lr = lr  # learning from consensus
        self.group_size = group_size
        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.teams = []
        for i in range(self.n // self.group_size):
            team = Team(m=self.m, index=i, alpha=self.alpha, reality=self.reality)
            for _ in range(self.group_size):
                individual = Individual(m=self.m, s=self.s, alpha=self.alpha, reality=self.reality, lr=self.lr)
                team.individuals.append(individual)
            self.teams.append(team)
        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []
        self.gini_across_time = []
        self.reward_num_across_time = []

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
        self.gini_across_time.append(0)

    def incentive_search(self, threshold_ratio=None, incentive=1, inactive_rate=None):
        new_consensus = []
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)
        for individual in individuals:
            if np.random.uniform(0, 1) < inactive_rate:
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
        # Once there is a change in consensus, reward the contributor
        reward_count = 0
        for old_bit, new_bit, index in zip(self.consensus, new_consensus, range(self.policy_num)):
            if old_bit != new_bit:
                reward_count += 1
                for individual in individuals:
                    if (individual.policy[index] == new_bit) and (individual.active == 1):  # individual active and vote correctly
                        individual.token += incentive / self.policy_num
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
        self.gini_across_time.append(self.get_gini())
        self.reward_num_across_time.append(reward_count)

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


if __name__ == '__main__':
    m = 60
    s = 1
    n = 280
    search_loop = 100
    lr = 0.3
    alpha = 3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, s=s, version="Rushed", alpha=3)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size, alpha=3)
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

    # Gini Index
    plt.plot(x, dao.gini_across_time, "k-", label="DAO")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Gini Index', fontweight='bold', fontsize=10)
    plt.title('Gini Index')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("DAO_gini.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Reward number
    plt.plot(x, dao.reward_num_across_time, "k-", label="DAO")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Reward Number', fontweight='bold', fontsize=10)
    plt.title('Reward Number')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("DAO_gini.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()



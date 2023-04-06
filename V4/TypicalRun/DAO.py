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
import pickle


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
        # self.performance_across_time = []
        # self.variance_across_time = []
        # self.diversity_across_time = []
        # self.consensus_performance_across_time = []

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
        # performance_list = []
        # for team in self.teams:
        #     performance_list += [individual.payoff for individual in team.individuals]
        #
        # self.performance_across_time.append(sum(performance_list) / len(performance_list))
        # self.variance_across_time.append(np.std(performance_list))
        # self.diversity_across_time.append(self.get_diversity())
        # self.consensus_performance_across_time.append(self.consensus_payoff)

    def incentive_search(self, threshold_ratio=None, incentive=1):
        new_consensus = []
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)
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
        # Once there is a change in consensus, reward the contributor
        for old_bit, new_bit, index in zip(self.consensus, new_consensus, range(self.policy_num)):
            if old_bit != new_bit:
                for individual in individuals:
                    if individual.policy[index] == new_bit:
                        individual.token += incentive / self.policy_num
        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)
        # 1) Generate and 2) adjust the superior majority view and then 3) learn from it
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()
        # performance_list = []
        # for team in self.teams:
        #     performance_list += [individual.payoff for individual in team.individuals]
        #
        # self.performance_across_time.append(sum(performance_list) / len(performance_list))
        # self.variance_across_time.append(np.std(performance_list))
        # self.diversity_across_time.append(self.get_diversity())
        # self.consensus_performance_across_time.append(self.consensus_payoff)

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
                    individual.turnover(turnover_rate=turnover_rate)


if __name__ == '__main__':
    m = 90
    s = 1
    n = 1225
    search_loop = 500
    lr = 0.3
    alpha = 3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, s=s, version="Rushed", alpha=alpha)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, group_size=group_size, alpha=alpha)
    individual_performance_list = []
    consensus_performance_list = []
    for _ in range(search_loop):
        individual_performance = []
        for team in dao.teams:
            individual_performance += [individual.payoff for individual in team.individuals]
        individual_performance_list.append(individual_performance)
        consensus_performance_list.append(dao.consensus_payoff)
        dao.search(threshold_ratio=0.5)

    with open("dao_typical_run", 'wb') as out_file:
        pickle.dump(individual_performance_list, out_file)
    with open("dao_consensus_typical_run", 'wb') as out_file:
        pickle.dump(consensus_performance_list, out_file)
# -*- coding: utf-8 -*-
# @Author   : Junyi
# @FileName: Hybrid.py
# Observing PEP 8 coding style
"""
Hybrid organizational form.

This class preserves the conceptual distinction between two channels of
organizational code formation:

1. Decentralized channel: token-weighted consensus among individuals.
2. Hierarchical channel: centralized specification through the managerial layer.

The parameter beta captures the degree of decentralization. In each search
period, organizational code is formed by decentralized consensus with
probability beta and by hierarchical specification with probability 1 - beta.

In the baseline implementation, managers do not vote in the consensus channel.
This keeps the two mechanisms analytically separate. Managerial voting can be
added later as a separate extension.
"""

import math
import time

import numpy as np

from Individual import Individual
from Reality import Reality
from Superior import Superior
from Team import Team


class Hybrid:
    def __init__(self, m=None, n=None, reality=None, lr=None, alpha=3,
                 group_size=None, beta=0.5, p1=0.1, p2=0.9, manager_num=50):
        """
        :param m: problem space size
        :param n: number of lower-level individuals
        :param reality: environment used to provide feedback
        :param lr: individual learning rate
        :param alpha: aggregation degree from belief to policy
        :param group_size: number of individuals under each manager/team
        :param beta: probability that code is formed by consensus
        :param p1: manager learning from organization code
        :param p2: organizational code learning from superior managers
        :param manager_num: number of managers; auto-adjusted if inconsistent
        """
        if m is None or n is None or group_size is None:
            raise ValueError("m, n, and group_size must be specified.")
        if m % alpha != 0:
            raise ValueError("m is not dividable by {0}".format(alpha))
        if not 0 <= beta <= 1:
            raise ValueError("beta must be between 0 and 1.")

        self.m = m
        self.n = n
        self.reality = reality
        self.lr = lr
        self.alpha = alpha
        self.policy_num = self.m // self.alpha
        self.group_size = group_size
        self.beta = beta
        self.manager_num = manager_num

        if self.manager_num * self.group_size != self.n:
            print("auto-adjust the unfit manager_num")
            self.manager_num = self.n // self.group_size

        if self.manager_num * self.group_size != self.n:
            raise ValueError("n must be divisible by group_size.")

        self.superior = Superior(policy_num=self.policy_num,
                                 reality=self.reality,
                                 manager_num=self.manager_num,
                                 p1=p1,
                                 p2=p2)

        self.teams = []
        for i in range(self.manager_num):
            team = Team(m=self.m, index=i, alpha=self.alpha,
                        reality=self.reality)
            for _ in range(self.group_size):
                individual = Individual(m=self.m, alpha=self.alpha,
                                        reality=self.reality, lr=self.lr)
                team.individuals.append(individual)
            team.manager = self.superior.managers[i]
            self.teams.append(team)

        # Organizational code states
        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.last_mode = None

        # DVs and diagnostic histories
        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []
        self.cv_across_time = []
        self.entropy_across_time = []
        self.antagonism_across_time = []
        self.consensus_performance_across_time = []
        self.mode_across_time = []

    def search(self, threshold_ratio=None, token=False, beta=None):
        """
        One period of hybrid search.

        With probability beta, the organization uses DAO-style consensus.
        With probability 1 - beta, it uses hierarchy-style centralized specification.

        :param threshold_ratio: voting threshold used in the consensus channel
        :param token: whether consensus is token-weighted
        :param beta: optional period-specific decentralization probability
        """
        if threshold_ratio is None:
            raise ValueError("threshold_ratio must be specified.")

        effective_beta = self.beta if beta is None else beta
        if not 0 <= effective_beta <= 1:
            raise ValueError("beta must be between 0 and 1.")

        if np.random.uniform(0, 1) < effective_beta:
            self._consensus_search(threshold_ratio=threshold_ratio, token=token)
            self.last_mode = "consensus"
        else:
            self._hierarchy_search()
            self.last_mode = "hierarchy"

        self._record_performance()

    def _consensus_search(self, threshold_ratio=None, token=True):
        """
        DAO-style channel: individuals specify the consensus through voting.
        """
        new_consensus = []
        individuals = self._get_individuals()

        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(
                belief=individual.belief)

        if not token:
            threshold = threshold_ratio * self.n
            for i in range(self.policy_num):
                crowd_opinion = [individual.policy[i]
                                 for individual in individuals]
                positive_count = sum([1 for each in crowd_opinion
                                      if each == 1])
                negative_count = sum([1 for each in crowd_opinion
                                      if each == -1])
                if (positive_count > threshold) and sum(crowd_opinion) > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and sum(crowd_opinion) < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)
        else:
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
        self.consensus_payoff = self.reality.get_policy_payoff(policy=self.consensus)

        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()

    def _hierarchy_search(self):
        """Hierarchy-style channel: managers (or delegators?) specify the consensus."""
        self.superior.search()
        self.consensus = self.superior.code.copy()
        self.consensus_payoff = self.reality.get_policy_payoff(policy=self.consensus)
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()

    def _record_performance(self):
        performance_list = [individual.payoff for team in self.teams for individual in team.individuals]
        mean_payoff = np.mean(performance_list)

        self.performance_across_time.append(mean_payoff)
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)
        self.mode_across_time.append(self.last_mode)

        if mean_payoff == 0:
            self.cv_across_time.append(0)
        else:
            self.cv_across_time.append(np.var(performance_list) / mean_payoff)

        self.entropy_across_time.append(self.get_entropy_binary())
        self.antagonism_across_time.append(self.get_antagonism_binary())

    def _get_individuals(self):
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        return individuals

    def get_diversity(self):
        diversity = 0
        individuals = self._get_individuals()
        belief_pool = [individual.belief for individual in individuals]
        for index, individual in enumerate(individuals):
            selected_pool = belief_pool[index + 1::]
            one_pair_diversity = [self.get_distance(individual.belief, belief)
                                  for belief in selected_pool]
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
            for manager in self.superior.managers:
                manager.turnover(turnover_rate=turnover_rate)

    def experimentation(self, experimentation_rate=None):
        if experimentation_rate:
            for team in self.teams:
                for individual in team.individuals:
                    individual.experimentation(
                        experimentation_rate=experimentation_rate)
            for manager in self.superior.managers:
                manager.experimentation(
                    experimentation_rate=experimentation_rate)

    def get_entropy_binary(self):
        individuals = self._get_individuals()
        belief_matrix = np.array([ind.belief for ind in individuals])
        _, m = belief_matrix.shape

        entropies = []
        for dim in range(m):
            beliefs_dim = belief_matrix[:, dim]
            _, counts = np.unique(beliefs_dim, return_counts=True)
            probs = counts / len(beliefs_dim)
            entropy = -np.sum([p * math.log(p) for p in probs if p > 0])
            entropies.append(entropy)

        return np.mean(entropies)

    def get_antagonism_binary(self):
        individuals = self._get_individuals()
        belief_matrix = np.array([ind.belief for ind in individuals],
                                 dtype=int)
        _, m = belief_matrix.shape

        antagonism_values = []
        for j in range(m):
            col = belief_matrix[:, j]
            nz = col[col != 0]
            if nz.size == 0:
                antagonism_values.append(0.0)
                continue

            p = np.mean(nz == 1)
            antagonism_values.append(4.0 * p * (1.0 - p))

        return float(np.mean(antagonism_values))


if __name__ == '__main__':
    t0 = time.time()
    m = 60
    n = 350
    lr = 0.3
    alpha = 3
    group_size = 7
    p1 = 0.1
    p2 = 0.9
    beta = 0.5
    search_iteration = 100

    reality = Reality(m=m, alpha=alpha)
    hybrid = Hybrid(m=m, n=n, reality=reality, lr=lr, alpha=alpha,
                    group_size=group_size, beta=beta, p1=p1, p2=p2)

    for i in range(search_iteration):
        hybrid.search(threshold_ratio=0.5, token=False)
        print(i, hybrid.last_mode)

    import matplotlib.pyplot as plt

    x = range(search_iteration)
    plt.plot(x, hybrid.performance_across_time, "k-", label="Mean")
    plt.plot(x, hybrid.consensus_performance_across_time, "r-",
             label="Consensus Code")
    plt.title('Performance')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Hybrid_performance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, hybrid.diversity_across_time, "k-", label="Hybrid")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    plt.title('Diversity')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Hybrid_diversity.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, hybrid.variance_across_time, "k-", label="Hybrid")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Hybrid_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
    print("END")

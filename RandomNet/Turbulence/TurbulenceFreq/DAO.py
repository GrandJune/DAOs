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
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size=None,
                 alpha=3):
        """
        :param m: problem space
        :param n: the number of agents
        :param reality: to provide feedback
        """
        self.m = m  # state length
        self.n = n  # the number of subunits under this superior
        self.alpha = alpha  # The aggregation degree
        self.policy_num = self.m // self.alpha
        self.reality = reality
        self.lr = lr  # learning from consensus
        self.group_size = group_size
        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.individuals = []
        for i in range(self.n):
            individual = Individual(m=self.m, alpha=self.alpha, reality=self.reality, lr=self.lr)
            self.individuals.append(individual)
        self.form_network()
        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []

    def form_network(self):
        for individual in self.individuals:
            individual.connections = np.random.choice(range(self.n), self.group_size, replace=False)

    def search(self, threshold_ratio=None, token=False):
        # Consensus Formation
        new_consensus = []
        if not token:
            threshold = threshold_ratio * self.n
            for i in range(self.policy_num):
                crowd_opinion = [individual.policy[i] for individual in self.individuals]
                positive_count = sum([1 for each in crowd_opinion if each == 1])
                negative_count = sum([1 for each in crowd_opinion if each == -1])
                if (positive_count > threshold) and sum(crowd_opinion) > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and sum(crowd_opinion) < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)

        else:  # With token
            threshold = threshold_ratio * sum([individual.token for individual in self.individuals])
            for i in range(self.policy_num):
                overall_sum = sum([individual.policy[i] * individual.token for individual in self.individuals])
                positive_count = sum([individual.token for individual in self.individuals if individual.policy[i] == 1])
                negative_count = sum([individual.token for individual in self.individuals if individual.policy[i] == -1])
                if (positive_count > threshold) and overall_sum > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and overall_sum < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)
        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)
        for individual in self.individuals:
            # 1) Generate Majority View
            superior_belief_pool = []
            for connect in individual.connections:
                if self.individuals[connect].payoff > individual.payoff:
                    superior_belief_pool.append(self.individuals[connect].belief)
            if len(superior_belief_pool) == 0:
                # The best performing actors will not learn from peers
                continue
            individual.form_superior_majority_view(superior_belief_pool=superior_belief_pool)
            # 2) Adjust Majority View to Consensus
            individual.adjust_majority_view_2_consensus(consensus=self.consensus)
            # 3) Learn From Adjusted Majority View
            individual.learning_from_belief(belief=individual.superior_majority_view)
        performance_list = [individual.payoff for individual in self.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

    def incentive_search(self, threshold_ratio=None, incentive=1):
        new_consensus = []
        threshold = threshold_ratio * sum([individual.token for individual in self.individuals])
        for i in range(self.policy_num):
            overall_sum = sum([individual.policy[i] * individual.token for individual in self.individuals])
            positive_count = sum([individual.token for individual in self.individuals if individual.policy[i] == 1])
            negative_count = sum([individual.token for individual in self.individuals if individual.policy[i] == -1])
            if (positive_count > threshold) and overall_sum > 0:
                new_consensus.append(1)
            elif (negative_count > threshold) and overall_sum < 0:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)
        # Once there is a change in consensus, reward the contributor
        for old_bit, new_bit, index in zip(self.consensus, new_consensus, range(self.policy_num)):
            if old_bit != new_bit:
                for individual in self.individuals:
                    if individual.policy[index] == new_bit:
                        individual.token += incentive / self.policy_num
        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)
        for individual in self.individuals:
            # 1) Generate Majority View
            superior_belief_pool = []
            for connect in individual.connections:
                if self.individuals[connect].payoff > individual.payoff:
                    superior_belief_pool.append(self.individuals[connect].belief)
            individual.form_superior_majority_view(superior_belief_pool=superior_belief_pool)
            # 2) Adjust Majority View to Consensus
            individual.adjust_majority_view_2_consensus(consensus=self.consensus)
            # 3) Learn From Adjusted Majority View
            individual.learning_from_belief(belief=individual.superior_majority_view)
        performance_list = [individual.payoff for individual in self.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

    def get_diversity(self):
        diversity = 0
        belief_pool = [individual.belief for individual in self.individuals]
        for index, individual in enumerate(self.individuals):
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
            for individual in self.individuals:
                individual.turnover(turnover_rate=turnover_rate)


if __name__ == '__main__':
    m = 60
    n = 350
    search_loop = 100
    lr = 0.3
    alpha = 5
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, version="Rushed", alpha=alpha)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, alpha=alpha)
    # dao.teams[0].individuals[0].belief = reality.real_code.copy()
    # dao.teams[0].individuals[0].payoff = reality.get_payoff(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].payoff)
    for period in range(search_loop):
        dao.search(threshold_ratio=0.5)
        print(dao.consensus)
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
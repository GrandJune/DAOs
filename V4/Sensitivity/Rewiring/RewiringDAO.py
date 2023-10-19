# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from RewiringIndividual import Individual
from Reality import Reality
import numpy as np


class DAO:
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size=None,
                 alpha=3, beta=0.2):
        """
        Consider the rewiring prob. such that one may learn from outside resource in the absence of consensus
        :param m: reality dimension
        :param n: crowd size
        :param reality:
        :param lr: learning rate
        :param group_size:
        :param alpha: aggregation level from belief to policy
        :param beta: rewiring probability from Fang's (2010) paper
        """
        self.m = m  # state length
        self.n = n  # the number of subunits under this superior
        if self.m % alpha != 0:
            raise ValueError("m is not dividable by {0}".format(alpha))
        self.alpha = alpha  # The aggregation degree
        self.policy_num = self.m // self.alpha
        self.reality = reality
        self.lr = lr  # learning from consensus
        self.group_size = group_size
        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.individuals = []
        for index in range(self.n):
            individual = Individual(m=self.m, alpha=self.alpha, reality=self.reality, lr=self.lr)
            individual.index = index
            individual.cluster = index // self.group_size
            self.individuals.append(individual)
        # form and rewiring the network
        self.beta = beta
        self.form_network()
        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []

    def form_network(self):
        # connections within the cluster (minimal connectivity)
        for index, individual in enumerate(self.individuals):
            individual.connections = [0] * self.n
            # the range is [0, 50), [50, 100), etc.
            for link_index in range(individual.cluster * self.group_size, (individual.cluster+1) * self.group_size):
                individual.connections[link_index] = 1

        # Rewire the connection
        for individual in self.individuals:
            ones_index = [index for index, value in enumerate(individual.connections) if value == 1]
            for index in ones_index:
                if np.random.uniform(0, 1) < self.beta:
                    zeros_index = [index for index, value in enumerate(individual.connections) if value == 0]
                    zeros_index = [each for each in zeros_index if each not in ones_index]  # rule out the previous "1";
                    # avoid rewiring back to previous connections (1 -> 0 -> 1)
                    if len(zeros_index) != 0:
                        selected_index = np.random.choice(zeros_index, p=[1 / len(zeros_index)] * len(zeros_index))
                        individual.connections[selected_index] = 1
                        individual.connections[index] = 0

    def search(self, threshold_ratio=None, token=False):
        # Consensus Formation
        new_consensus = []
        for individual in self.individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)

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
        # 1) Generate and 2) adjust the superior majority view and then 3) learn from it
        # for team in self.teams:
        #     team.form_individual_majority_view()
        #     team.adjust_majority_view_2_consensus(policy=self.consensus)
        #     team.learn()
        for individual in self.individuals:
            connected_superior_belief = [self.individuals[index].belief for index in individual.connections
                                if self.individuals[index].payoff > individual.payoff]
            if len(connected_superior_belief) == 0:
                continue
            individual.form_majority_view(belief_pool=connected_superior_belief)
            individual.adjust_majority_view_2_consensus(policy=new_consensus)
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
    alpha = 3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, version="Rushed", alpha=alpha)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, alpha=alpha, beta=0.3)
    # for individual in dao.individuals:
    #     connect = []
    #     for index, value in enumerate(individual.connections):
    #         if value == 1:
    #             connect.append(index)
    #     original_connect = list(range(individual.cluster * group_size, (individual.cluster+1) * group_size))
    #     print(connect, original_connect)

    for period in range(search_loop):
        dao.search(threshold_ratio=0.5)
        print(dao.consensus)
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



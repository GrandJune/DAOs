# -*- coding: utf-8 -*-
# @Time     : 24/01/2024 19:05
# @Author   : Junyi
# @FileName: Hierarchy.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual import Individual
import numpy as np
import math
from Reality import Reality
from Superior import Superior
from Team import Team
import time


class Hierarchy:
    def __init__(self, m=None, n=None, reality=None, lr=None, alpha=3,
                 group_size=None, p1=0.1, p2=0.9, manager_num=50, confirmation=True):
        """
        :param m: problem space
        :param s: the first complexity
        :param t: the second complexity
        :param n: the number of agents
        :param reality: to provide feedback
        """
        self.m = m  # state length
        self.n = n
        self.manager_num = manager_num
        self.group_size = group_size
        self.confirmation = confirmation  # whether or the lower-level individual initially confirm to the upper-level
        if self.manager_num * self.group_size != self.n:
            print("auto-adjust the unfit manager_num")
            self.manager_num = self.n // self.group_size
        self.alpha = alpha
        self.policy_num = self.m // self.alpha
        self.lr = lr  # learning rate
        self.reality = reality
        manager_num = self.n // self.group_size
        self.superior = Superior(policy_num=self.policy_num, reality=self.reality, manager_num=manager_num, p1=p1, p2=p2)
        # n is the number of managers, instead of employers;  In March's paper, n=50
        # p1, p2 is set to be the best one in March's paper
        self.individuals = []
        for i in range(self.n):
            individual = Individual(m=self.m, alpha=self.alpha, reality=self.reality, lr=self.lr)
            self.individuals.append(individual)
        self.form_network()
        # DVs
        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []
        self.superior_performance_across_time = []

    def form_network(self):
        # define individuals' connections
        for individual in self.individuals:
            individual.connections = np.random.choice(range(self.n), self.group_size, replace=False)
        # define managers' scope
        manager_positions = np.random.choice(range(self.n), self.manager_num, replace=False)
        for index, manager in enumerate(self.superior.managers):
            manager.scope = self.individuals[manager_positions[index]].connections.copy()
        # Enforce Supervision
        for manager in self.superior.managers:
            for index in manager.scope:
                self.individuals[index].adjust_belief_2_supervision(policy=manager.policy)

    def search(self):
        # Managers Search
        self.superior.search()
        # Enforce Supervision from Managers
        for manager in self.superior.managers:
            for index in manager.scope:
                self.individuals[index].adjust_belief_2_supervision(policy=manager.policy)
        # Supervised team learning
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
            # 2) Learn From Majority View
            individual.learning_from_belief(belief=individual.superior_majority_view)
        performance_list = [individual.payoff for individual in self.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())

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
            self.superior.turnover(turnover_rate=turnover_rate)
            for individual in self.individuals:
                individual.turnover(turnover_rate=turnover_rate)
            # Enforce Supervision
            for manager in self.superior.managers:
                for index in manager.scope:
                    self.individuals[index].adjust_belief_2_supervision(policy=manager.policy)


if __name__ == '__main__':
    t0 = time.time()
    m = 60
    s = 1
    n = 350  # 50 managers, each manager control one autonomous team; 50*7=350
    lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    p1 = 0.1  # belief learning from code
    p2 = 0.9  # code learning from belief
    search_iteration = 100
    reality = Reality(m=m)
    hierarchy = Hierarchy(m=m, n=n, reality=reality, lr=lr, group_size=group_size, p1=p1, p2=p2)
    for i in range(search_iteration):
        hierarchy.search()
        print(i)
    import matplotlib.pyplot as plt
    x = range(search_iteration)
    plt.plot(x, hierarchy.performance_across_time, "k-", label="Mean")
    plt.plot(x, hierarchy.superior.performance_average_across_time, "r-", label="Superior")
    plt.title('Performance')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Hierarchy_performance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()


    plt.plot(x, hierarchy.diversity_across_time, "k-", label="Hierarchy")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    plt.title('Diversity')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Hierarchy_diversity.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, hierarchy.variance_across_time, "k-", label="Hierarchy")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Hierarchy_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
    print("END")





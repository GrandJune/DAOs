# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality


class Superior:
    def __init__(self, m=None, n=None, reality=None, p1=None, p2=None):
        """
        March's model to model how the traditional organizational cognition is formed.
        :param m: problem dimension (the length of policy directives, i.e., m // s)
        :param n: group size, 50 in March's model
        :param reality: policy reality
        :param p1: code learning from belief
        :param p2: belief learning from code
        """
        self.m = m  # policy length
        self.n = n  # the number of subunits under this superior
        self.p1 = p1  # code learning from belief, 0.9
        self.p2 = p2  # belief learning from code, 0.1
        self.reality = reality
        self.managers = []
        for _ in range(self.n):
            manager = Manager(m=self.m, reality=self.reality)
            self.managers.append(manager)
        self.policy = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)
        self.performance_across_time = []
        self.diversity_across_time = []

    def search(self):
        superior_policy = []
        for manager in self.managers:
            if manager.payoff > self.payoff:
                superior_policy.append(manager.policy)
        if len(superior_policy) != 0:
            majority_policy = self.get_majority_view(superior_policy=superior_policy)
            # socialization effectiveness
            for index in range(self.m):
                if self.policy[index] != majority_policy[index]:
                    if np.random.uniform(0, 1) < self.p1:
                        self.policy[index] = majority_policy[index]
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)
        # learning effectiveness
        for manager in self.managers:
            for index in range(self.m):
                if manager.policy[index] != self.policy[index]:
                    if np.random.uniform(0, 1) < self.p2:
                        manager.policy[index] = self.policy[index]
            manager.payoff = self.reality.get_policy_payoff(policy=manager.policy)
        self.performance_across_time.append(self.payoff)

    def get_majority_view(self, superior_policy=None):
        majority_view = []
        for i in range(self.m):
            temp = [policy[i] for policy in superior_policy]
            if sum(temp) > 0:
                majority_view.append(1)
            elif sum(temp) < 0:
                majority_view.append(-1)
            else:
                majority_view.append(0)
        return majority_view


class Manager:
    def __init__(self, m=None, reality=None, ):
        self.m = m
        self.reality = reality
        self.policy = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.payoff = self.reality.get_policy_payoff(policy=self.policy)


if __name__ == '__main__':
    m = 120
    s = 3
    n = 200
    p1 = 0.5
    p2 = 0.1
    reality = Reality(m=m, s=s)
    superior = Superior(m=m//s, n=n, reality=reality, p1=p1, p2=p2)
    performance_list = []
    for _ in range(300):
        superior.search()
        # print(superior.payoff)
        performance_list.append(superior.payoff)
    import matplotlib.pyplot as plt
    x = range(300)
    plt.plot(x, performance_list, "k-", label="Hierarchy")
    # plt.title('Diversity Decrease')+
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Diversity_Comparison_s3.png", transparent=True, dpi=1200)
    plt.show()

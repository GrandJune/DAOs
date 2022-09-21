# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 19:53
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import math
from itertools import permutations
import numpy as np
from Reality import Reality


class Individual:
    def __init__(self, m=None, s=None, reality=None, lr=None):
        self.m = m
        self.s = s
        self.lr = lr  # learning rate, learning from consensus
        self.token = None
        self.connections = []  # for autonomy, to seek for superior subgroup
        self.reality = reality
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.policy = self.reality.belief_2_policy(belief=self.belief)  # a fake policy for voting
        self.payoff = self.reality.get_payoff(belief=self.belief)

    def learning_from_consensus(self, consensus=None):
        for index in range(self.m):
            if np.random.uniform(0, 1) < self.lr:
                self.belief[index] = self.reality.policy_2_belief(policy=consensus[index])
        self.payoff = self.reality.get_payoff(belief=self.belief)


    def learning_from_authority(self, policy=None, authority=None):
        pass

    def confirm_to_supervision(self, policy=None, authority=None):
        """
        No search effect, just determine whether to confirm or not for each domain
        :param policy: The policy constraint to which agents need to confirm
        :param confirm: The authority degree; To what extend the agents need to confirm to superiors' policy directives
        :return: A confirmation situation under the authority degree of confirm
        """
        for index, value in enumerate(policy):
            if value == 0:
                continue
            if value == self.policy[index]:
                continue
            else:
                if np.random.uniform(0, 1) <= authority:
                    alternatives = [value] * math.ceil(self.s / 2) + [-1 * value] * (self.s - math.ceil(self.s / 2))
                    alternatives = list(set(permutations(alternatives)))
                    alternatives.append([value] * self.s)
                    belief_pieces = alternatives[np.random.choice(len(alternatives))]
                    self.belief[index*self.s:(index+1)*self.s] = belief_pieces
        self.payoff = self.reality.get_payoff(belief=self.belief)
        self.policy = self.reality.belief_2_policy(belief=self.belief)


if __name__ == '__main__':
    m = 10
    s = 2
    t = 1
    n = 4
    version = "Weighted"
    reality = Reality(m=m, s=s, version=version)
    individual = Individual(m=m, s=s, t=t, reality=reality)
    # for _ in range(100):
    #     individual.free_local_search()
    #     print(individual.belief)
    #     print(individual.payoff)
    #     print("-------------")
    belief_test = reality.real_code.copy()
    belief_test[-1] = -1 * belief_test[-1]
    print(belief_test)
    payoff_test = reality.get_payoff(belief_test)
    print(payoff_test)
    # print("individual.belief: ", individual.belief, individual.payoff)
    # # policy_list = [1, -1, 1, -1, 1, -1, 1, -1, 1]
    # policy_list = reality.real_policy
    # for _ in range(10):
    #     for index, policy in enumerate(policy_list):
    #         individual.constrained_local_search_under_authority(focal_policy=policy, focal_policy_index=index, authority=0.8)
    #         print(individual.belief, individual.payoff)


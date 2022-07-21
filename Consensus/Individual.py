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
    def __init__(self, m=None, s=None, t=None, reality=None):
        self.m = m
        self.s = s
        self.t = t
        self.belief = np.random.choice([-1, 0, 1], self.m, p=[1/3, 1/3, 1/3])
        self.reality = reality
        self.policy = self.reality.belief_2_policy(belief=self.belief)  # a fake policy as a variable temp
        self.payoff = self.reality.get_hierarchy_payoff_rushed(belief=self.belief, policy=self.policy)

    def constrained_local_search(self, focal_policy=None, focal_policy_index=None):
        """
        The local search should confirm to the policy constraint
        :param focal_policy: 1 or -1
        :param focal_policy_index: the index of the policy (0, self.m/self.s)
        :return:
        """
        if focal_policy == 0:
            self.free_local_search(scope=range(focal_policy_index*self.s, (focal_policy_index+1)*self.s))
            return
        next_belief = self.belief.copy()
        alternatives = [focal_policy] * math.ceil(self.s / 2) + [-1*focal_policy] * (self.s - math.ceil(self.s / 2))
        alternatives = list(set(permutations(alternatives, self.s)))
        alternatives.append([focal_policy] * self.s)
        # print("alternatives: ", alternatives)
        # print("focal_policy_index: ", focal_policy_index)
        for next_belief_pieces in alternatives:
            next_belief[focal_policy_index*self.s:(focal_policy_index+1)*self.s] = next_belief_pieces
            next_payoff = self.reality.get_rushed_payoff(belief=next_belief)
            if next_payoff > self.payoff:
                self.previous_payoff = self.payoff
                self.previous_belief = self.belief.copy()
                self.belief = next_belief
                self.payoff = next_payoff
                break

    def free_local_search(self, scope=None):
        if not scope:
            scope = range(self.m)
        next_belief = self.belief.copy()
        focal_index = np.random.choice(scope)
        if next_belief[focal_index] == 0:
            next_belief[focal_index] = np.random.choice([-1, 1])
        else:
            next_belief[focal_index] *= -1
        next_policy = self.reality.belief_2_policy(belief=self.belief)
        next_payoff = self.reality.get_hierarchy_payoff_rushed(belief=next_belief, policy=next_policy)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            self.policy = next_policy

    def confirm_to_supervision(self, policy=None):
        """
        NO search, just an initialization for the blinding between superior and manager
        :param policy:
        :return:
        """
        for index, value in enumerate(policy):
            alternatives = [value] * math.ceil(self.s / 2) + [-1 * value] * (self.s - math.ceil(self.s / 2))
            alternatives = list(set(permutations(alternatives)))
            # print(alternatives)
            alternatives.append([value] * self.s)
            belief_pieces = alternatives[np.random.choice(len(alternatives))]
            self.belief[index*self.s:(index+1)*self.s] = belief_pieces


if __name__ == '__main__':
    m = 27
    s = 3
    t = 3
    n = 4
    reality = Reality(m=m, s=s, t=t)
    individual = Individual(m=m, s=s, t=t, reality=reality)
    print("individual.belief: ", individual.belief, individual.payoff)
    policy_list = [1, -1, 1, -1, 1, -1, 1, -1, 1]
    for index, policy in enumerate(policy_list):
        individual.constrained_local_search(focal_policy=policy, focal_policy_index=index)
    print(individual.belief, individual.payoff)

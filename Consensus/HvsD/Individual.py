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
        self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

    def constrained_local_search(self, focal_policy=None, focal_policy_index=None, version="Rushed"):
        """
        The local search should confirm to the policy constraint
        :param focal_policy: 1 or -1
        :param focal_policy_index: the index of the policy (0, self.m/self.s)
        :return:
        """
        if focal_policy == 0:
            self.free_local_search(scope=range(focal_policy_index*self.s, (focal_policy_index+1)*self.s), version=version)
            return
        next_belief = self.belief.copy()
        alternatives = [focal_policy] * math.ceil(self.s / 2) + [-1*focal_policy] * (self.s - math.ceil(self.s / 2))
        alternatives = list(set(permutations(alternatives, self.s)))
        alternatives.append([focal_policy] * self.s)
        # print("alternatives: ", alternatives)
        # print("focal_policy_index: ", focal_policy_index)
        next_belief_pieces = alternatives[np.random.choice(len(alternatives))]
        next_belief[focal_policy_index*self.s:(focal_policy_index+1)*self.s] = next_belief_pieces
        next_policy = self.reality.belief_2_policy(belief=next_belief)
        # next_payoff = self.reality.get_hierarchy_payoff_rushed(policy=self.policy, belief=next_belief, version=version)
        next_payoff = self.reality.get_belief_payoff(belief=next_belief, version=version)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.policy = next_policy
            self.payoff = next_payoff
            self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

    def free_local_search(self, scope=None, version="Rushed"):
        if not scope:
            scope = range(self.m)
        next_belief = self.belief.copy()
        focal_index = np.random.choice(scope)
        if next_belief[focal_index] == 0:
            next_belief[focal_index] = np.random.choice([-1, 1])  # Another way is to make the knowledge scope fixed
            # return
        else:
            next_belief[focal_index] *= -1
        next_policy = self.reality.belief_2_policy(belief=next_belief)
        # next_payoff = self.reality.get_hierarchy_payoff_rushed(belief=next_belief, policy=next_policy, version=version)
        next_payoff = self.reality.get_belief_payoff(belief=next_belief, version=version)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            self.policy = next_policy
            self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

    def confirm_to_supervision(self, policy=None):
        """
        NO search, just an initialization for the blinding between superior and manager
        :param policy:
        :return:
        """
        for index, value in enumerate(policy):
            if value == 0:
                continue
            elif value != self.policy[index]:  # Only confirm the conflicting beliefs
                alternatives = [value] * math.ceil(self.s / 2) + [-1 * value] * (self.s - math.ceil(self.s / 2))
                alternatives = list(set(permutations(alternatives)))
                alternatives.append([value] * self.s)
                belief_pieces = alternatives[np.random.choice(len(alternatives))]
                self.belief[index*self.s:(index+1)*self.s] = belief_pieces
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)


if __name__ == '__main__':
    m = 27
    s = 3
    t = 3
    n = 4
    alpha = 0.5
    reality = Reality(m=m, s=s, t=t, alpha=alpha)
    individual = Individual(m=m, s=s, t=t, reality=reality)
    print("individual.belief: ", individual.belief, individual.payoff)
    policy_list = [1, -1, 1, -1, 1, -1, 1, -1, 1]
    for index, policy in enumerate(policy_list):
        individual.constrained_local_search(focal_policy=policy, focal_policy_index=index, version="Rushed")
    print(individual.belief, individual.payoff)


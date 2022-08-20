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
        self.payoff = self.reality.get_belief_payoff(belief=self.belief)
        self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

    def constrained_local_search_under_consensus(self, focal_policy=None, focal_policy_index=None):
        """
        The local search should confirm to the policy constraint
        :param focal_policy: 1 or -1
        :param focal_policy_index: the index of the policy (0, self.m/self.s)
        :return:
        """
        if focal_policy == 0:
            self.free_local_search(scope=range(focal_policy_index*self.s, (focal_policy_index+1)*self.s))
            return
        next_belief_under_consensus, next_belief_under_autonomy = self.belief.copy(), self.belief.copy()
        # Under consensus
        alternatives = [focal_policy] * math.ceil(self.s / 2) + [-1*focal_policy] * (self.s - math.ceil(self.s / 2))
        alternatives = list(set(permutations(alternatives, self.s)))
        alternatives.append([focal_policy] * self.s)
        # print("alternatives: ", alternatives)
        # print("focal_policy_index: ", focal_policy_index)
        next_belief_pieces = alternatives[np.random.choice(len(alternatives))]
        next_belief_under_consensus[focal_policy_index*self.s:(focal_policy_index+1)*self.s] = next_belief_pieces
        next_policy_under_consensus = self.reality.belief_2_policy(belief=next_belief_under_consensus)
        next_payoff_under_consensus = self.reality.get_belief_payoff(belief=next_belief_under_consensus)

        # Under autonomy
        focal_index = np.random.choice(range(focal_policy_index*self.s, (focal_policy_index+1)*self.s))
        if next_belief_under_autonomy[focal_index] != 0:
            next_belief_under_autonomy[focal_index] *= -1
        else:
            next_belief_under_autonomy[focal_index] = np.random.choice([-1, 1])
        next_policy_under_autonomy = self.reality.belief_2_policy(belief=next_belief_under_autonomy)
        next_payoff_under_autonomy = self.reality.get_belief_payoff(belief=next_belief_under_autonomy)

        max_payoff = max(next_payoff_under_autonomy, next_payoff_under_consensus, self.payoff)

        if self.payoff == max_payoff:
            return
        elif next_payoff_under_autonomy == max_payoff:
            self.belief = next_belief_under_autonomy
            self.policy = next_policy_under_autonomy
            self.payoff = next_payoff_under_autonomy
            self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)
        else:
            self.belief = next_belief_under_consensus
            self.policy = next_policy_under_consensus
            self.payoff = next_payoff_under_consensus
            self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

    def constrained_local_search_under_authority(self, focal_policy=None, focal_policy_index=None, authority=None):
        """
        The local search should confirm to the policy constraint
        :param focal_policy: 1 or -1
        :param focal_policy_index: the index of the policy (0, self.m/self.s)
        :return:
        """
        if focal_policy == 0:
            self.free_local_search(scope=range(focal_policy_index*self.s, (focal_policy_index+1)*self.s))
            return
        next_belief_under_authority, next_belief_under_autonomy = self.belief.copy(), self.belief.copy()
        if np.random.uniform(0, 1) <= authority:
            # Under Authority
            alternatives = [focal_policy] * math.ceil(self.s / 2) + [-1*focal_policy] * (self.s - math.ceil(self.s / 2))
            alternatives = list(set(permutations(alternatives, self.s)))
            alternatives.append([focal_policy] * self.s)
            next_belief_pieces = alternatives[np.random.choice(len(alternatives))]
            # print("alternatives: ", alternatives, focal_policy)
            next_belief_under_authority[focal_policy_index*self.s:(focal_policy_index+1)*self.s] = next_belief_pieces
            next_policy_under_authority = self.reality.belief_2_policy(belief=next_belief_under_authority)
            next_payoff_under_authority = self.reality.get_belief_payoff(belief=next_belief_under_authority)
            if next_payoff_under_authority > self.payoff:
                self.belief = next_belief_under_authority
                self.policy = next_policy_under_authority
                self.payoff = next_payoff_under_authority
                self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)
        else:
            # Under autonomy
            focal_index = np.random.choice(range(focal_policy_index * self.s, (focal_policy_index + 1) * self.s))
            if next_belief_under_autonomy[focal_index] != 0:
                next_belief_under_autonomy[focal_index] *= -1
            else:
                next_belief_under_autonomy[focal_index] = np.random.choice([-1, 1])
            next_policy_under_autonomy = self.reality.belief_2_policy(belief=next_belief_under_autonomy)
            next_payoff_under_autonomy = self.reality.get_belief_payoff(belief=next_belief_under_autonomy)
            if next_payoff_under_autonomy > self.payoff:
                self.belief = next_belief_under_autonomy
                self.policy = next_policy_under_autonomy
                self.payoff = next_payoff_under_autonomy
                self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

    def free_local_search(self, scope=None):
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
        next_payoff = self.reality.get_belief_payoff(belief=next_belief)
        if next_payoff > self.payoff:
            self.belief = next_belief
            self.payoff = next_payoff
            self.policy = next_policy
            self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)

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
        self.policy = self.reality.belief_2_policy(belief=self.belief)
        self.policy_payoff = self.reality.get_policy_payoff(policy=self.policy)


if __name__ == '__main__':
    m = 10
    s = 2
    t = 1
    n = 4
    version = "Rushed"
    reality = Reality(m=m, s=s, t=t, version=version)
    individual = Individual(m=m, s=s, t=t, reality=reality)
    for _ in range(10):
        print(individual.belief, individual.payoff)
        individual.free_local_search()
    # print("individual.belief: ", individual.belief, individual.payoff)
    # # policy_list = [1, -1, 1, -1, 1, -1, 1, -1, 1]
    # policy_list = reality.real_policy
    # for _ in range(10):
    #     for index, policy in enumerate(policy_list):
    #         individual.constrained_local_search_under_authority(focal_policy=policy, focal_policy_index=index, authority=0.8)
    #         print(individual.belief, individual.payoff)


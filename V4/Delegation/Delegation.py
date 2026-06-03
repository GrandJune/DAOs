# -*- coding: utf-8 -*-
# @Author   : Junyi
# @FileName: Delegation.py
# Observing PEP 8 coding style
"""
Delegative DAO organizational form.

This class minimally extends the baseline DAO class by introducing one
additional parameter: delegation_rate. The parameter captures the proportion
of members who delegate their voting rights rather than voting directly.

The extension preserves the baseline organizational learning architecture:

1. Individuals form policies from their beliefs.
2. Organizational code is formed through voting-based consensus.
3. Teams adjust their majority view toward the enacted consensus.
4. Individuals learn from the adjusted majority view.

The only changed component is the voting aggregation layer. Delegators do not
vote directly; instead, their voting weight is transferred to selected direct
voters. Delegates remain ordinary DAO members rather than managers or a
separate hierarchical layer.

Three delegate-selection modes are supported:

1. random: delegators randomly select a direct voter.
2. performance: delegators are more likely to select higher-performing voters.
3. similarity: delegators are more likely to select direct voters
   whose beliefs are more similar to their own.

Delegation is allowed across groups.
"""

import math
import time

import numpy as np

from Individual import Individual
from Reality import Reality
from Team import Team


class Delegation:
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size=None,
                 alpha=3, delegation_rate=0, similarity_threshold=0.5):
        """
        :param m: problem space
        :param n: number of agents
        :param reality: environment used to provide feedback
        :param lr: individual learning rate
        :param group_size: number of individuals in each autonomous group
        :param alpha: aggregation degree from belief to policy
        :param delegation_rate: probability that an individual delegates voting rights
        :param similarity_threshold: minimum belief similarity required for
            similarity-based delegation
        """
        if m is None or n is None or group_size is None:
            raise ValueError("m, n, and group_size must be specified.")
        if m % alpha != 0:
            raise ValueError("m is not dividable by {0}".format(alpha))
        if not 0 <= delegation_rate <= 1:
            raise ValueError("delegation_rate must be between 0 and 1.")
        if not 0 <= similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between 0 and 1.")

        self.m = m
        self.n = n
        self.reality = reality
        self.lr = lr
        self.group_size = group_size
        self.alpha = alpha
        self.policy_num = self.m // self.alpha
        self.delegation_rate = delegation_rate
        self.similarity_threshold = similarity_threshold

        self.consensus = [0] * self.policy_num
        self.consensus_payoff = 0
        self.teams = []
        for i in range(self.n // self.group_size):
            team = Team(m=self.m, index=i, alpha=self.alpha,
                        reality=self.reality)
            for _ in range(self.group_size):
                individual = Individual(m=self.m, alpha=self.alpha,
                                        reality=self.reality, lr=self.lr)
                team.individuals.append(individual)
            self.teams.append(team)

        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []
        self.cv_across_time = []
        self.entropy_across_time = []
        self.antagonism_across_time = []

    def search(self, threshold_ratio=None, token=False, delegation_rate=None,
               delegation_mode="random", similarity_threshold=None):
        """
        One period of delegative DAO search.

        :param threshold_ratio: voting threshold used for consensus formation
        :param token: whether baseline voting weight comes from token holdings
        :param delegation_rate: optional period-specific delegation rate
        :param delegation_mode: "random", "performance", or "similarity"
        :param similarity_threshold: optional period-specific minimum belief
            similarity required for similarity-based delegation
        """
        if threshold_ratio is None:
            raise ValueError("threshold_ratio must be specified.")

        effective_delegation_rate = (self.delegation_rate if delegation_rate is None
                                     else delegation_rate)
        if not 0 <= effective_delegation_rate <= 1:
            raise ValueError("delegation_rate must be between 0 and 1.")
        effective_similarity_threshold = (self.similarity_threshold
                                          if similarity_threshold is None
                                          else similarity_threshold)
        if not 0 <= effective_similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between 0 and 1.")

        valid_modes = ["random", "performance", "similarity"]
        if delegation_mode not in valid_modes:
            raise ValueError(
                "delegation_mode must be 'random', 'performance', "
                "or 'similarity'."
            )

        # Consensus Formation
        new_consensus = []
        individuals = self._get_individuals()

        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(
                belief=individual.belief)

        base_weights = self._get_base_weights(individuals=individuals,
                                              token=token)
        effective_weights = self._get_effective_weights(
            individuals=individuals,
            base_weights=base_weights,
            delegation_rate=effective_delegation_rate,
            delegation_mode=delegation_mode,
            similarity_threshold=effective_similarity_threshold)

        threshold = threshold_ratio * sum(base_weights)

        for i in range(self.policy_num):
            overall_sum = sum([individual.policy[i] * effective_weights[index]
                               for index, individual in enumerate(individuals)])
            positive_count = sum([effective_weights[index]
                                  for index, individual in enumerate(individuals)
                                  if individual.policy[i] == 1])
            negative_count = sum([effective_weights[index]
                                  for index, individual in enumerate(individuals)
                                  if individual.policy[i] == -1])
            if (positive_count > threshold) and overall_sum > 0:
                new_consensus.append(1)
            elif (negative_count > threshold) and overall_sum < 0:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)

        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(
            policy=new_consensus)

        # 1) Generate and 2) adjust the majority view and then 3) learn from it
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()

        self._record_performance()

    def _get_base_weights(self, individuals=None, token=False):
        if token:
            return [individual.token for individual in individuals]
        return [1 for _ in individuals]

    def _get_effective_weights(self, individuals=None, base_weights=None,
                               delegation_rate=None, delegation_mode="random",
                               similarity_threshold=0.5):
        """
        Convert baseline voting weights into effective voting weights after
        delegation.

        Delegators transfer their full voting weight to direct voters. Direct
        voters retain their own voting weight and may receive delegated weight.
        Under similarity-based delegation, if no direct voter is sufficiently
        similar, the delegator remains inactive and the weight is not cast.
        """
        effective_weights = base_weights.copy()
        n = len(individuals)

        delegator_indices = [index for index in range(n)
                             if np.random.uniform(0, 1) < delegation_rate]
        direct_voter_indices = [index for index in range(n)
                                if index not in delegator_indices]

        # Avoid a degenerate period in which no one casts votes directly.
        if len(direct_voter_indices) == 0:
            retained_index = np.random.choice(delegator_indices)
            delegator_indices.remove(retained_index)
            direct_voter_indices.append(retained_index)

        for delegator_index in delegator_indices:
            # The delegator first becomes inactive. The vote is restored only
            # if a valid delegate is selected. In similarity mode, no valid
            # delegate means the voting weight is not cast in this period.
            effective_weights[delegator_index] = 0

            delegate_index = self._select_delegate(
                individuals=individuals,
                delegator_index=delegator_index,
                candidate_indices=direct_voter_indices,
                delegation_mode=delegation_mode,
                similarity_threshold=similarity_threshold)

            if delegate_index is None:
                continue

            effective_weights[delegate_index] += base_weights[delegator_index]

        return effective_weights

    def _select_delegate(self, individuals=None, delegator_index=None,
                         candidate_indices=None, delegation_mode="random",
                         similarity_threshold=0.5):
        """
        Select one delegate from direct voters. Return None when no valid
        delegate is available.
        """
        if len(candidate_indices) == 0:
            return None
        if delegation_mode == "random":
            return np.random.choice(candidate_indices)

        if delegation_mode == "performance":
            candidate_payoffs = np.array([individuals[index].payoff
                                          for index in candidate_indices],
                                         dtype=float)

            # Payoffs are usually non-negative. The shift below keeps the
            # method robust if experimentation or environmental change
            # produces unusual values.
            min_payoff = np.min(candidate_payoffs)
            if min_payoff < 0:
                candidate_payoffs = candidate_payoffs - min_payoff

            if np.sum(candidate_payoffs) == 0:
                probabilities = np.ones(len(candidate_indices)) / len(candidate_indices)
            else:
                probabilities = candidate_payoffs / np.sum(candidate_payoffs)

            return np.random.choice(candidate_indices, p=probabilities)

        if delegation_mode == "similarity":
            delegator_belief = individuals[delegator_index].belief
            candidate_similarities = np.array(
                [self._get_belief_similarity(delegator_belief,
                                             individuals[index].belief)
                 for index in candidate_indices],
                dtype=float)

            valid_positions = np.where(
                candidate_similarities >= similarity_threshold)[0]
            if len(valid_positions) == 0:
                return None

            valid_candidate_indices = [candidate_indices[position]
                                       for position in valid_positions]
            valid_similarities = candidate_similarities[valid_positions]

            if np.sum(valid_similarities) == 0:
                probabilities = (np.ones(len(valid_candidate_indices)) /
                                 len(valid_candidate_indices))
            else:
                probabilities = valid_similarities / np.sum(valid_similarities)

            return np.random.choice(valid_candidate_indices, p=probabilities)

    def _get_belief_similarity(self, belief_a=None, belief_b=None):
        """
        Return belief similarity as one minus normalized Hamming distance.
        """
        distance = self.get_distance(belief_a, belief_b)
        return 1 - distance / self.m

    def _record_performance(self):
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]

        mean_payoff = np.mean(performance_list)
        self.performance_across_time.append(mean_payoff)
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

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

    def experimentation(self, experimentation_rate=None):
        if experimentation_rate:
            for team in self.teams:
                for individual in team.individuals:
                    individual.experimentation(
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
    n = 280
    search_loop = 300
    lr = 0.3
    alpha = 3
    group_size = 7
    delegation_rate = 0.5

    reality = Reality(m=m, version="Rushed", alpha=alpha)
    delegation = Delegation(m=m, n=n, reality=reality, lr=lr,
                            group_size=group_size, alpha=alpha,
                            delegation_rate=delegation_rate)

    for period in range(search_loop):
        delegation.search(threshold_ratio=0.5, token=False,
                          delegation_mode="random")
        # delegation.search(threshold_ratio=0.5, token=False,
        #                   delegation_mode="performance")
        # delegation.search(threshold_ratio=0.5, token=False,
        #                   delegation_mode="similarity")
        print("--{0}--".format(period))

    import matplotlib.pyplot as plt
    x = range(search_loop)

    plt.plot(x, delegation.performance_across_time, "k-", label="Mean")
    plt.plot(x, delegation.consensus_performance_across_time, "r-",
             label="Consensus")
    plt.title('Performance')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Delegation_performance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, delegation.diversity_across_time, "k-", label="Delegation")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    plt.title('Diversity')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Delegation_diversity.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    plt.plot(x, delegation.variance_across_time, "k-", label="Delegation")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.savefig("Delegation_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
    print("END")

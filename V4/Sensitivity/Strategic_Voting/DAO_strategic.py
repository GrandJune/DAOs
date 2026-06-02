# -*- coding: utf-8 -*-
# @Time     : 6/2/2026
# @Author   : Junyi
# @FileName: DAO_strategic.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual import Individual
from Team import Team
from Reality import Reality
import math
import numpy as np


class DAOStrategic:
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size=None,
                 alpha=3):
        """
        :param m: problem space
        :param n: the number of agents
        :param reality: to provide feedback

        This robustness-check class implements a lightweight version of
        strategic voting. It does not model full game-theoretic optimization
        or equilibrium reasoning. Instead, it introduces a strategic voting
        parameter that captures the probability that an individual aligns
        their vote with the currently perceived majority position rather than
        voting sincerely according to their own belief.

        This preserves the original organizational-learning structure while
        relaxing the baseline assumption that voting behavior directly reflects
        individual beliefs.
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
        self.teams = []
        for i in range(self.n // self.group_size):
            team = Team(m=self.m, index=i, alpha=self.alpha, reality=self.reality)
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

        # Additional diagnostics for the strategic-voting robustness check.
        self.switch_count_across_time = []
        self.switch_rate_across_time = []

    def _get_individuals(self):
        """Return all lower-level individuals in the DAO."""
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        return individuals

    @staticmethod
    def _validate_strategic_rate(strategic_rate):
        """Ensure the strategic voting parameter is a probability."""
        if strategic_rate is None:
            strategic_rate = 0
        if strategic_rate < 0 or strategic_rate > 1:
            raise ValueError("strategic_rate must be between 0 and 1.")
        return strategic_rate

    def _get_perceived_majority(self, individuals=None, weights=None,
                                policy_index=None, active_only=False):
        """
        Identify the currently perceived majority position for a policy
        dimension.

        The majority is calculated from sincere votes before strategic
        adjustment. If active_only=True, only active voters are included.
        """
        positive_count = 0
        negative_count = 0

        for individual, weight in zip(individuals, weights):
            if active_only and individual.active != 1:
                continue
            if individual.policy[policy_index] == 1:
                positive_count += weight
            elif individual.policy[policy_index] == -1:
                negative_count += weight

        if positive_count > negative_count:
            return 1
        elif negative_count > positive_count:
            return -1
        else:
            return 0

    def _get_strategic_votes(self, individuals=None, weights=None,
                             policy_index=None, strategic_rate=0,
                             active_only=False):
        """
        Generate votes after strategic adjustment.

        With probability strategic_rate, an individual aligns with the
        currently perceived majority position. Otherwise, the individual votes
        sincerely according to their own policy belief. If no clear perceived
        majority exists, voting remains sincere.
        """
        perceived_majority = self._get_perceived_majority(
            individuals=individuals,
            weights=weights,
            policy_index=policy_index,
            active_only=active_only
        )

        votes = []
        switch_count = 0
        eligible_count = 0

        for individual in individuals:
            sincere_vote = individual.policy[policy_index]

            if active_only and individual.active != 1:
                votes.append(sincere_vote)
                continue

            eligible_count += 1
            strategic_vote = sincere_vote

            if perceived_majority != 0:
                if np.random.uniform(0, 1) < strategic_rate:
                    strategic_vote = perceived_majority

            if strategic_vote != sincere_vote:
                switch_count += 1

            votes.append(strategic_vote)

        return votes, switch_count, eligible_count

    def search(self, threshold_ratio=None, strategic_rate=0):
        """
        Consensus formation under strategic voting.

        Compared with the baseline token-weighted voting rule in DAO.py,
        this version allows individuals to strategically align their vote with
        the currently perceived majority position with probability
        strategic_rate. Token weights remain linear; only vote expression is
        modified.
        """
        if threshold_ratio is None:
            raise ValueError("threshold_ratio must be specified.")
        strategic_rate = self._validate_strategic_rate(strategic_rate)

        new_consensus = []
        individuals = self._get_individuals()

        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(
                belief=individual.belief)

        weights = [individual.token for individual in individuals]
        threshold = threshold_ratio * sum(weights)

        total_switch_count = 0
        total_eligible_count = 0

        for i in range(self.policy_num):
            votes, switch_count, eligible_count = self._get_strategic_votes(
                individuals=individuals,
                weights=weights,
                policy_index=i,
                strategic_rate=strategic_rate,
                active_only=False
            )

            total_switch_count += switch_count
            total_eligible_count += eligible_count

            overall_sum = sum([vote * weight
                               for vote, weight in zip(votes, weights)])
            positive_count = sum([weight for vote, weight in zip(votes, weights)
                                  if vote == 1])
            negative_count = sum([weight for vote, weight in zip(votes, weights)
                                  if vote == -1])

            if (positive_count > threshold) and overall_sum > 0:
                new_consensus.append(1)
            elif (negative_count > threshold) and overall_sum < 0:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)

        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(
            policy=new_consensus)

        # 1) Generate, 2) adjust the majority view, and 3) learn from it.
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()

        self._record_performance()

        self.switch_count_across_time.append(total_switch_count)
        if total_eligible_count == 0:
            self.switch_rate_across_time.append(0)
        else:
            self.switch_rate_across_time.append(
                total_switch_count / total_eligible_count)

    def incentive_search(self, threshold_ratio=None, incentive=1,
                         inactive_rate=None, strategic_rate=0):
        """
        Incentive/participation extension under strategic voting.

        Active voters may strategically align their vote with the currently
        perceived majority position with probability strategic_rate. The
        participation logic is otherwise kept parallel to the baseline DAO
        implementation.
        """
        if threshold_ratio is None:
            raise ValueError("threshold_ratio must be specified.")
        if inactive_rate is None:
            inactive_rate = 0
        strategic_rate = self._validate_strategic_rate(strategic_rate)

        new_consensus = []
        individuals = self._get_individuals()

        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(
                belief=individual.belief)

        for individual in individuals:
            if np.random.uniform(0, 1) < inactive_rate:
                if np.random.uniform(0, 1) < incentive:
                    individual.active = 1
                else:
                    individual.active = 0
            else:
                individual.active = 1

        weights = [individual.token for individual in individuals]
        threshold = threshold_ratio * sum(weights)

        total_switch_count = 0
        total_eligible_count = 0

        for i in range(self.policy_num):
            votes, switch_count, eligible_count = self._get_strategic_votes(
                individuals=individuals,
                weights=weights,
                policy_index=i,
                strategic_rate=strategic_rate,
                active_only=True
            )

            total_switch_count += switch_count
            total_eligible_count += eligible_count

            overall_sum = sum([vote * weight * individual.active
                               for vote, weight, individual in
                               zip(votes, weights, individuals)])
            positive_count = sum([weight for vote, weight, individual in
                                  zip(votes, weights, individuals)
                                  if (vote == 1) and (individual.active == 1)])
            negative_count = sum([weight for vote, weight, individual in
                                  zip(votes, weights, individuals)
                                  if (vote == -1) and (individual.active == 1)])

            if (positive_count > threshold) and overall_sum > 0:
                new_consensus.append(1)
            elif (negative_count > threshold) and overall_sum < 0:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)

        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(
            policy=new_consensus)

        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()

        self._record_performance()

        self.switch_count_across_time.append(total_switch_count)
        if total_eligible_count == 0:
            self.switch_rate_across_time.append(0)
        else:
            self.switch_rate_across_time.append(
                total_switch_count / total_eligible_count)

    def _record_performance(self):
        """Record the same dependent variables as the baseline DAO class."""
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff
                                 for individual in team.individuals]

        mean_performance = np.mean(performance_list)
        self.performance_across_time.append(mean_performance)
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

        if mean_performance == 0:
            self.cv_across_time.append(0)
        else:
            self.cv_across_time.append(np.var(performance_list) /
                                       mean_performance)

        self.entropy_across_time.append(self.get_entropy_binary())
        self.antagonism_across_time.append(self.get_antagonism_binary())

    def get_diversity(self):
        diversity = 0
        individuals = []
        for team in self.teams:
            individuals += team.individuals
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
        """
        Compute average Shannon entropy across dimensions, considering
        {-1, 0, 1} beliefs. Entropy is higher when beliefs are more evenly
        distributed across possible positions.
        """
        individuals = []
        for team in self.teams:
            individuals += team.individuals

        belief_matrix = np.array([ind.belief for ind in individuals])
        n, m = belief_matrix.shape

        entropies = []
        for dim in range(m):
            beliefs_dim = belief_matrix[:, dim]
            values, counts = np.unique(beliefs_dim, return_counts=True)
            probs = counts / len(beliefs_dim)
            H = -np.sum([p * math.log(p) for p in probs if p > 0])
            entropies.append(H)

        return np.mean(entropies)

    def get_antagonism_binary(self):
        """
        Compute average binary antagonism across dimensions, considering only
        {-1, 1} beliefs and ignoring 0's.

        Per dimension:
            p = share of +1 among non-zero beliefs
            A = 4 * p * (1 - p)
        """
        individuals = [ind for team in self.teams for ind in team.individuals]
        belief_matrix = np.array([ind.belief for ind in individuals], dtype=int)
        n, m = belief_matrix.shape

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
    m = 60
    n = 280
    search_loop = 300
    lr = 0.3
    alpha = 3
    group_size = 7  # the smallest group size in Fang's model: 7
    strategic_rate = 0.3

    reality = Reality(m=m, version="Rushed", alpha=3)
    dao = DAOStrategic(m=m, n=n, reality=reality, lr=lr,
                       group_size=group_size, alpha=3)

    for team in dao.teams:
        for individual in team.individuals:
            individual.token = 1

    for period in range(search_loop):
        dao.search(threshold_ratio=0.5, strategic_rate=strategic_rate)
        print("--{0}--".format(period))

    import matplotlib.pyplot as plt
    x = range(search_loop)

    plt.plot(x, dao.performance_across_time, "k-", label="Mean")
    plt.plot(x, dao.consensus_performance_across_time, "r-", label="Consensus")
    plt.title('Performance')
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.show()
    plt.clf()

    plt.plot(x, dao.diversity_across_time, "k-", label="DAO")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    plt.title('Diversity')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.show()
    plt.clf()

    plt.plot(x, dao.variance_across_time, "k-", label="DAO")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.show()
    plt.clf()

    plt.plot(x, dao.switch_rate_across_time, "k-", label="Strategic Switch Rate")
    plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    plt.ylabel('Switch Rate', fontweight='bold', fontsize=10)
    plt.title('Strategic Voting Switch Rate')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.show()
    plt.clf()

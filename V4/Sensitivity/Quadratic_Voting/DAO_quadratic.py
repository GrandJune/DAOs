# -*- coding: utf-8 -*-
# @Time     : 5/23/2026 19:05
# @Author   : Junyi
# @FileName: DAO_quadratic.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import math
from Individual import Individual
from Team import Team
from Reality import Reality
import numpy as np


class DAOQuadratic:
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size=None,
                 alpha=3):
        """
        :param m: problem space
        :param n: the number of agents
        :param reality: to provide feedback

        This robustness-check class implements a lightweight version of
        quadratic voting. It does not model strategic vote-credit allocation
        or preference intensity. Instead, it uses a concave transformation of
        token holdings as effective voting weight: sqrt(token). This preserves
        the original organizational-learning structure while reducing the
        marginal voting influence of large token holders.
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
                individual = Individual(m=self.m, alpha=self.alpha, reality=self.reality, lr=self.lr)
                team.individuals.append(individual)
            self.teams.append(team)
        self.performance_across_time = []
        self.variance_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []
        self.cv_across_time = []
        self.entropy_across_time = []
        self.antagonism_across_time = []

    def _get_individuals(self):
        """Return all lower-level individuals in the DAO."""
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        return individuals

    @staticmethod
    def _quadratic_weight(token):
        """
        Convert token holdings into quadratic-voting weight.

        This is the lightweight robustness-check interpretation of quadratic
        voting: effective influence increases with token holdings, but at a
        decreasing marginal rate. For example, a voter with 100 tokens has
        effective weight 10 rather than 100.
        """
        return math.sqrt(max(token, 0))

    def search(self, threshold_ratio=None):
        """
        Consensus formation under quadratic voting.

        Compared with the baseline token-weighted voting rule in DAO.py,
        this version replaces each individual's linear token weight with
        sqrt(token). This keeps the rest of the learning process unchanged.
        """
        if threshold_ratio is None:
            raise ValueError("threshold_ratio must be specified.")

        new_consensus = []
        individuals = self._get_individuals()

        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(
                belief=individual.belief)

        weights = [self._quadratic_weight(individual.token)
                   for individual in individuals]
        threshold = threshold_ratio * sum(weights)

        for i in range(self.policy_num):
            overall_sum = sum([individual.policy[i] * weight
                               for individual, weight in zip(individuals, weights)])
            positive_count = sum([weight for individual, weight in zip(individuals, weights)
                                  if individual.policy[i] == 1])
            negative_count = sum([weight for individual, weight in zip(individuals, weights)
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

        # 1) Generate, 2) adjust the majority view, and 3) learn from it.
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()

        self._record_performance()

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

    def incentive_search(self, threshold_ratio=None, incentive=1,
                         inactive_rate=None):
        """
        Incentive/participation extension under quadratic voting.

        Active voters' effective weights are sqrt(token), rather than token.
        The participation logic is otherwise kept parallel to the baseline
        DAO implementation.
        """
        if threshold_ratio is None:
            raise ValueError("threshold_ratio must be specified.")
        if inactive_rate is None:
            inactive_rate = 0

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

        weights = [self._quadratic_weight(individual.token)
                   for individual in individuals]
        threshold = threshold_ratio * sum(weights)

        for i in range(self.policy_num):
            overall_sum = sum([individual.policy[i] * weight * individual.active
                               for individual, weight in zip(individuals, weights)])
            positive_count = sum([weight for individual, weight in zip(individuals, weights)
                                  if (individual.policy[i] == 1) and
                                  (individual.active == 1)])
            negative_count = sum([weight for individual, weight in zip(individuals, weights)
                                  if (individual.policy[i] == -1) and
                                  (individual.active == 1)])
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

    def get_diversity(self):
        diversity = 0
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        belief_pool = [individual.belief for individual in individuals]
        for index, individual in enumerate(individuals):
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
                    individual.experimentation(experimentation_rate=experimentation_rate)

    def get_entropy_binary(self):
        """
        Compute average Shannon entropy across dimensions,
        considering only {-1, 1} beliefs and ignoring 0's.
        Entropy is maximal when -1 and 1 are equally common
        among non-zero beliefs.
        """
        individuals = []
        for team in self.teams:
            individuals += team.individuals

        belief_matrix = np.array([ind.belief for ind in individuals])
        n, m = belief_matrix.shape

        entropies = []
        for dim in range(m):
            # Take all beliefs for this dimension (including zeros)
            beliefs_dim = belief_matrix[:, dim]

            # Count frequency of -1, 0, and 1 (or any values present)
            values, counts = np.unique(beliefs_dim, return_counts=True)
            probs = counts / len(beliefs_dim)

            # Shannon entropy (natural log)
            H = -np.sum([p * math.log(p) for p in probs if p > 0])
            entropies.append(H)

        return np.mean(entropies)

    def get_antagonism_binary(self):
        """
        Compute average binary antagonism across dimensions,
        considering only {-1, 1} beliefs and ignoring 0's (neutral opinions).

        Per dimension:
            p = share of +1 among non-zero beliefs
            A = 4 * p * (1 - p)   # ranges from 0 (unanimity) to 1 (perfect two-camp balance)
        """
        # Collect all individuals' beliefs into an array: shape (n, m)
        individuals = [ind for team in self.teams for ind in team.individuals]
        belief_matrix = np.array([ind.belief for ind in individuals], dtype=int)
        n, m = belief_matrix.shape

        antagonism_values = []
        for j in range(m):
            col = belief_matrix[:, j]
            nz = col[col != 0]  # ignore neutrals
            if nz.size == 0:
                antagonism_values.append(0.0)  # no extremes, so antagonism = 0
                continue

            p = np.mean(nz == 1)  # fraction of +1 among non-zeros
            antagonism_values.append(4.0 * p * (1.0 - p))

        return float(np.mean(antagonism_values))


if __name__ == '__main__':
    m = 60
    n = 280
    search_loop = 300
    lr = 0.3
    alpha = 3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, version="Rushed", alpha=3)
    dao = DAOQuadratic(m=m, n=n, reality=reality, lr=lr, group_size=group_size, alpha=3)

    # Assign equal token holdings for the standalone test.
    # In the full experiment, this is usually handled by assign_tokens().
    for team in dao.teams:
        for individual in team.individuals:
            individual.token = 1

    # dao.teams[0].individuals[0].belief = reality.real_code.copy()
    # dao.teams[0].individuals[0].payoff = reality.get_payoff(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].belief)
    # print(dao.teams[0].individuals[0].payoff)
    for period in range(search_loop):
        dao.search(threshold_ratio=0.5)
        # print(period, dao.consensus, reality.real_policy, reality.real_code)
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

    # # Gini Index
    # plt.plot(x, dao.gini_across_time, "k-", label="DAO")
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Gini Index', fontweight='bold', fontsize=10)
    # plt.title('Gini Index')
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_gini.png", transparent=False, dpi=1200)
    # plt.show()
    # plt.clf()

    # Reward number
    # plt.plot(x, dao.reward_num_across_time, "k-", label="DAO")
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Reward Number', fontweight='bold', fontsize=10)
    # plt.title('Reward Number')
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_gini.png", transparent=False, dpi=1200)
    # plt.show()
    # plt.clf()



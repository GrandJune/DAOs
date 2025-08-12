# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import math
from Individual import Individual
from Team import Team
from Reality import Reality
import numpy as np


class DAO:
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size=None,
                 alpha=3):
        """
        :param m: problem space
        :param n: the number of agents
        :param reality: to provide feedback
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
        self.cv_across_time = []
        self.entropy_across_time = []
        self.antagonism_across_time = []
        self.diversity_across_time = []
        self.consensus_performance_across_time = []

    def search(self, threshold_ratio=None, token=False):
        # Consensus Formation
        new_consensus = []
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)

        if not token:
            threshold = threshold_ratio * self.n
            for i in range(self.policy_num):
                crowd_opinion = [individual.policy[i] for individual in individuals]
                positive_count = sum([1 for each in crowd_opinion if each == 1])
                negative_count = sum([1 for each in crowd_opinion if each == -1])
                if (positive_count > threshold) and sum(crowd_opinion) > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and sum(crowd_opinion) < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)

        else:  # With token
            threshold = threshold_ratio * sum([individual.token for individual in individuals])
            for i in range(self.policy_num):
                overall_sum = sum([individual.policy[i] * individual.token for individual in individuals])
                positive_count = sum([individual.token for individual in individuals if individual.policy[i] == 1])
                negative_count = sum([individual.token for individual in individuals if individual.policy[i] == -1])
                if (positive_count > threshold) and overall_sum > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and overall_sum < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)
        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)
        # 1) Generate and 2) adjust the superior majority view and then 3) learn from it
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
        cv = np.var(performance_list) / np.mean(performance_list)
        self.cv_across_time.append(cv)
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)
        self.entropy_across_time.append(self.get_entropy_binary())
        self.antagonism_across_time.append(self.get_antagonism_binary())

    def interrupted_search(self, threshold_ratio=None, current_iteration=None):
        # Consensus Formation
        new_consensus = []
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)

        threshold = threshold_ratio * self.n
        # only update consensus within a small time windows
        if current_iteration % 50 in range(0, 10):  # 10 iterations after each 50-step
            t = current_iteration % 50
            chunk_size = (self.policy_num + 9) // 10  # Ceiling division
            start_idx = t * chunk_size
            end_idx = min((t + 1) * chunk_size, self.policy_num)

            for i in range(start_idx, end_idx):
                crowd_opinion = [individual.policy[i] for individual in individuals]
                positive_count = sum([1 for each in crowd_opinion if each == 1])
                negative_count = sum([1 for each in crowd_opinion if each == -1])
                if (positive_count > threshold) and sum(crowd_opinion) > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and sum(crowd_opinion) < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)

            # Fill unchanged elements with existing consensus values
            for i in range(0, start_idx):
                new_consensus.append(self.consensus[i])
            for i in range(end_idx, self.policy_num):
                new_consensus.append(self.consensus[i])

            self.consensus = new_consensus
            self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)

            # 1) Generate and 2) adjust the superior majority view and then 3) learn from it
            for team in self.teams:
                team.form_individual_majority_view()
                team.adjust_majority_view_2_consensus(policy=self.consensus)
                team.learn()

        else:
            self.consensus = [0] * self.policy_num
            # autonomous learning
            for team in self.teams:
                team.form_individual_majority_view()
                # team.adjust_majority_view_2_consensus(policy=self.consensus)
                team.learn()
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]
        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
        cv = np.var(performance_list) / np.mean(performance_list)
        self.cv_across_time.append(cv)
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)
        self.entropy_across_time.append(self.get_entropy_binary())
        self.antagonism_across_time.append(self.get_antagonism_binary())

    def incentive_search(self, threshold_ratio=None, incentive=1, inactive_rate=None):
        new_consensus = []
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)
        for individual in individuals:
            if np.random.uniform(0, 1) < inactive_rate:  # if inactive, e.g., 0.2
                if np.random.uniform(0, 1) < incentive:   # if incentivized, e.g., 0.8
                    individual.active = 1
                else:
                    individual.active = 0
            else:
                individual.active = 1
        threshold = threshold_ratio * sum([individual.token for individual in individuals])
        # consider the active status
        for i in range(self.policy_num):
            overall_sum = sum([individual.policy[i] * individual.token * individual.active for individual in individuals])
            positive_count = sum([individual.token for individual in individuals if (individual.policy[i] == 1) and (individual.active == 1)])
            negative_count = sum([individual.token for individual in individuals if (individual.policy[i] == -1) and (individual.active == 1)])
            if (positive_count > threshold) and overall_sum > 0:
                new_consensus.append(1)
            elif (negative_count > threshold) and overall_sum < 0:
                new_consensus.append(-1)
            else:
                new_consensus.append(0)
        self.consensus = new_consensus
        self.consensus_payoff = self.reality.get_policy_payoff(policy=new_consensus)
        # 1) Generate and 2) adjust the superior majority view and 3) learn from it
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]

        self.performance_across_time.append(sum(performance_list) / len(performance_list))
        self.variance_across_time.append(np.std(performance_list))
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

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

    # newly added for formal measures of polarization
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
            # Extract only non-zero beliefs for this dimension
            nonzero_beliefs = belief_matrix[belief_matrix[:, dim] != 0, dim]
            total_nonzero = len(nonzero_beliefs)

            if total_nonzero == 0:
                entropies.append(0.0)  # No information if all are neutral
                continue

            # Count frequency of -1 and 1
            values, counts = np.unique(nonzero_beliefs, return_counts=True)
            probs = counts / total_nonzero

            # Shannon entropy for this dimension (natural log)
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
    m = 90 # policy_num = 20; every 50 iterations form a consensus -> need 1k iterations
    n = 350
    search_loop = 300
    lr = 0.3
    alpha = 3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, version="Rushed", alpha=3)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, alpha=3)

    for period in range(search_loop):
        previous_consensus = dao.consensus.copy()
        dao.search(threshold_ratio=0.5)
        if period % 100 == 0:
            print("-" * 10, period)

    import matplotlib.pyplot as plt
    x = range(search_loop)
    plt.plot(x, dao.performance_across_time, "k-", label="Mean")
    plt.plot(x, dao.consensus_performance_across_time, "r-", label="Consensus")
    plt.title('Performance')
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_performance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Diversity
    plt.plot(x, dao.diversity_across_time, "k-", label="DAO")
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    plt.title('Diversity')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_diversity.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Variance
    plt.plot(x, dao.variance_across_time, "k-", label="DAO")

    # Add shaded gray area for 10 iterations every 50 iterations
    for i in range(0, max(x) + 1, 50):
        plt.axvspan(i, i + 10, color='gray', alpha=0.2)  # adjust alpha for visibility

        # Optional: Add dashed lines at the start of each interval
        plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
        # Dashed line at the end
        plt.axvline(x=i + 10, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)

    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Coefficient of Variance
    plt.plot(x, dao.cv_across_time, "k-", label="DAO")

    # Add shaded gray area for 10 iterations every 50 iterations
    for i in range(0, max(x) + 1, 50):
        plt.axvspan(i, i + 10, color='gray', alpha=0.2)  # adjust alpha for visibility

        # Optional: Add dashed lines at the start of each interval
        plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
        # Dashed line at the end
        plt.axvline(x=i + 10, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)

    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Coefficient of Variance', fontweight='bold', fontsize=10)
    plt.title('Coefficient of Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_coefficient_of_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Entropy
    plt.plot(x, dao.entropy_across_time, "k-", label="DAO")

    # Add shaded gray area for 10 iterations every 50 iterations
    for i in range(0, max(x) + 1, 50):
        plt.axvspan(i, i + 10, color='gray', alpha=0.2)  # adjust alpha for visibility

        # Optional: Add dashed lines at the start of each interval
        plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
        # Dashed line at the end
        plt.axvline(x=i + 10, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)

    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Shannon Entropy', fontweight='bold', fontsize=10)
    plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_entropy.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()


    # Antagonism
    plt.plot(x, dao.entropy_across_time, "k-", label="DAO")

    # Add shaded gray area for 10 iterations every 50 iterations
    for i in range(0, max(x) + 1, 50):
        plt.axvspan(i, i + 10, color='gray', alpha=0.2)  # adjust alpha for visibility

        # Optional: Add dashed lines at the start of each interval
        plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
        # Dashed line at the end
        plt.axvline(x=i + 10, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)

    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Antagonism', fontweight='bold', fontsize=10)
    plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_antagonism.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

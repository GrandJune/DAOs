# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Individual_incentive import Individual
from Team_incentive import Team
from Reality import Reality
import numpy as np


class DAO:
    def __init__(self, m=None, n=None, reality=None, lr=None, group_size=None, alpha=3):
        """
        :param m: problem space
        :param n: the number of agents
        :param reality: to provide feedback
        """
        self.m = m  # state length
        self.n = n  # the number of individuals
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
        self.diversity_across_time.append(self.get_diversity())
        self.consensus_performance_across_time.append(self.consensus_payoff)

    def incentive_search(self, threshold_ratio=None, incentive=1.0, basic_active_rate=None, k=1):
        prior_performance_list = []
        for team in self.teams:
            prior_performance_list += [individual.payoff for individual in team.individuals]
        prior_performance = sum(prior_performance_list) / len(prior_performance_list)
        new_consensus = []
        individuals = []
        for team in self.teams:
            individuals += team.individuals
        for individual in individuals:
            individual.policy = self.reality.belief_2_policy(belief=individual.belief)
            # individuals are sensitive to the incentivized token amount in deciding whether to vote
            # endogenous asymmetry from incentive,
            # compared to exogenous asymmetry from many factors
            # unrelated to the value redistribution that comes with growth in organizational performance, such as investment factors, -> captured by exgogenous asymmetry
            x = individual.incentive
            sigmoid_output = x / (x + (1-x) * np.exp(- k * x))
            # linear_output = x * k
            prob_to_vote = basic_active_rate + sigmoid_output
            # modify Sigmoid func so that y=0 when x=1
            individual.prob_to_vote = prob_to_vote
            if np.random.uniform(0, 1) < prob_to_vote:
                individual.active = 1
            else:
                individual.active = 0
        prob_to_vote_list = []
        token_list = []
        active_list = []
        for individual in individuals:
            prob_to_vote_list.append(individual.prob_to_vote)
            token_list.append(individual.token)
            active_list.append(individual.active)

        threshold = threshold_ratio * sum([individual.token for individual in individuals])
        # consider the active status
        # if either party meet the threshold, select relative majority
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
        # identify the contributor
        for individual in individuals:
            for i in range(self.policy_num):
                if individual.policy[i] == self.consensus[i]:
                    individual.contribution += 1
        # 1) Generate and 2) adjust the superior majority view and 3) learn from it
        for team in self.teams:
            team.form_individual_majority_view()
            team.adjust_majority_view_2_consensus(policy=self.consensus)
            team.learn()  # only active voters will learn from consensus
        performance_list = []
        for team in self.teams:
            performance_list += [individual.payoff for individual in team.individuals]
        new_performance = sum(performance_list) / len(performance_list)
        performance_increment_ratio = (new_performance - prior_performance) / prior_performance  # ideally max: 1
        # The increment ratio/expansion should be mostly attributed/allocated to only active members
        if performance_increment_ratio > 0:  # if the value is added (for incentive rather than penalty)
            for individual in individuals:
                if individual.active == 1:
                    individual.incentive = incentive * performance_increment_ratio * individual.token * individual.contribution
                    individual.token *= (1 + incentive * performance_increment_ratio)
                    # token increments are equally allocate to only active members
                    individual.contribution = 0  # re-set
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

    def get_gini(self,):
        """
        Gini = 0: perfect equality; Gini = 1: extreme inequality
        :return:
        """
        token_list = []
        for team in self.teams:
            for individual in team.individuals:
                token_list.append(individual.token)
        # Ensure the array is a numpy array
        array = np.array(token_list)

        # If the array is empty or contains only zeros, return 0
        if array.size == 0 or np.all(array == 0):
            return 0

        # Sort the array in ascending order
        array = np.sort(array)

        # Get the number of elements in the array
        n = array.size

        # Calculate the Gini coefficient using the efficient formula
        numerator = np.sum((2 * np.arange(1, n + 1) - n - 1) * array)
        gini_index = numerator / (n * np.sum(array))

        return gini_index

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


if __name__ == '__main__':
    m = 30
    n = 280
    search_loop = 200
    lr = 0.3
    alpha = 3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, version="Rushed", alpha=3)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, alpha=3)
    asymmetry = 4
    mode = 200
    token_list = []
    individual_list = []
    for team in dao.teams:
        for individual in team.individuals:
            # individual.token = (np.random.pareto(a=asymmetry) + 1) * mode
            individual.token = mode
            token_list.append(individual.token)
            individual_list.append(individual)
    print("Token sum: ", sum(token_list), max(token_list))
    for period in range(search_loop):
        dao.incentive_search(threshold_ratio=0.4, incentive=1, basic_active_rate=0.9, k=1)
        active_sum, token_sum = 0, 0
        token_list = []
        for individual in individual_list:
            active_sum += individual.active
            token_list.append(individual.token)
        token_list = sorted(token_list)
        q1_value = np.percentile(token_list, 25)
        q3_value = np.percentile(token_list, 75)
        print("Q1 token: ", q1_value, "Q3 token: ", q3_value)
        max_indicator, q1_index, max_index = 0, 0, 0
        min_indicator, min_index = 100, 0
        for index, individual in enumerate(individual_list):
            if individual.token > max_indicator:
                max_indicator = individual.token
                max_index = index
            if individual.token < min_indicator:
                min_indicator = individual.token
                min_index = index
            if individual.token == q1_value:
                # print("Q1")
                q1_index = index
        # print("Max: ", max_indicator, "Q1: ", q1_value, "Min: ", min_indicator)
        # print(token_list)

        print(individual_list[max_index].prob_to_vote, individual_list[max_index].token,
              individual_list[max_index].incentive, individual_list[max_index].active)

        print(individual_list[min_index].prob_to_vote, individual_list[min_index].token,
              individual_list[min_index].incentive, individual_list[min_index].active)

        print(individual_list[q1_index].prob_to_vote, individual_list[q1_index].token,
              individual_list[q1_index].incentive, individual_list[q1_index].active)
        gini_index = dao.get_gini()
        print("active rate: ", active_sum / n, "Gini: ", gini_index)
        print("-" * 5)
    # import matplotlib.pyplot as plt
    # x = range(search_loop)
    #
    # plt.plot(x, dao.performance_across_time, "k-", label="Mean")
    # plt.plot(x, dao.consensus_performance_across_time, "r-", label="Consensus")
    # plt.title('Performance')
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Performance', fontweight='bold', fontsize=10)
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_performance.png", transparent=False, dpi=1200)
    # plt.show()
    # plt.clf()

    # Diversity
    # plt.plot(x, dao.diversity_across_time, "k-", label="DAO")
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    # plt.title('Diversity')
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_diversity.png", transparent=False, dpi=1200)
    # plt.show()
    # plt.clf()

    # Variance
    # plt.plot(x, dao.variance_across_time, "k-", label="DAO")
    # plt.xlabel('Iteration', fontweight='bold', fontsize=10)
    # plt.ylabel('Variance', fontweight='bold', fontsize=10)
    # plt.title('Variance')
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # # plt.savefig("DAO_variance.png", transparent=False, dpi=1200)
    # plt.show()
    # plt.clf()

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



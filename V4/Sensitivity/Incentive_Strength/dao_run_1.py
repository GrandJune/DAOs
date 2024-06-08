# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO import DAO
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Pool
from multiprocessing import Semaphore
import pickle
import math


def func(m=None, n=None, group_size=None, lr=None, incentive=None, active_rate=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size)
    # initially with equal token
    for team in dao.teams:
        for individual in team.individuals:
            individual.token = 1
    if incentive == 0:
        for _ in range(search_loop):
            dao.search(threshold_ratio=0.5)
    else:
        for _ in range(search_loop):
            new_consensus = []
            individuals = []
            for team in self.teams:
                individuals += team.individuals
            for individual in individuals:
                individual.policy = self.reality.belief_2_policy(belief=individual.belief)
            for individual in individuals:
                if np.random.uniform(0, 1) < active_rate:  # if active rate, e.g., 0.8
                    individual.active = 1
                else:
                    if np.random.uniform(0, 1) < incentive:  # if incentive into vote, e.g., 0.8
                        individual.active = 1
                    else:
                        individual.active = 0
            threshold = threshold_ratio * sum([individual.token for individual in individuals])
            # consider the active status
            for i in range(self.policy_num):
                overall_sum = sum(
                    [individual.policy[i] * individual.token * individual.active for individual in individuals])
                positive_count = sum([individual.token for individual in individuals if
                                      (individual.policy[i] == 1) and (individual.active == 1)])
                negative_count = sum([individual.token for individual in individuals if
                                      (individual.policy[i] == -1) and (individual.active == 1)])
                if (positive_count > threshold) and overall_sum > 0:
                    new_consensus.append(1)
                elif (negative_count > threshold) and overall_sum < 0:
                    new_consensus.append(-1)
                else:
                    new_consensus.append(0)
            # Once there is a change in consensus, reward the contributor
            for old_bit, new_bit, index in zip(self.consensus, new_consensus, range(self.policy_num)):
                if old_bit != new_bit:
                    for individual in individuals:
                        if (individual.policy[index] == new_bit) and (
                                individual.active == 1):  # individual active and vote correctly
                            individual.token += incentive
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
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time, dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    import os
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    repetition = 50
    incentive_list = [0.1, 0.2]
    active_rate_list = [0.9, 0.8, 0.7, 0.6]
    search_loop = 500
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 50
    for incentive in incentive_list:
        for active_rate in active_rate_list:
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, n, group_size, lr, incentive, active_rate, search_loop, loop, return_dict, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
            results = return_dict.values()  # Don't need dict index, since it is repetition.
            performance_across_repeat = [result[0] for result in results]
            consensus_across_repeat = [result[1] for result in results]
            diversity_across_repeat = [result[2] for result in results]
            variance_across_repeat = [result[3] for result in results]
            # After taking an average across repetitions
            performance_final = []
            consensus_final = []
            diversity_final = []
            variance_final = []
            for period in range(search_loop):
                performance_temp = [performance_list[period] for performance_list in performance_across_repeat]
                consensus_temp = [consensus_list[period] for consensus_list in consensus_across_repeat]
                diversity_temp = [diversity_list[period] for diversity_list in diversity_across_repeat]
                variance_temp = [variance_list[period] for variance_list in variance_across_repeat]

                performance_final.append(sum(performance_temp) / len(performance_temp))
                consensus_final.append(sum(consensus_temp) / len(consensus_temp))
                diversity_final.append(sum(diversity_temp) / len(diversity_temp))
                variance_final.append(sum(variance_temp) / len(variance_temp))

            performance_file_name = r"dao_performance_incentive_{0}_active_{1}".format(incentive, active_rate)
            delay = np.random.uniform(1, 20)
            time.sleep(delay)
            if os.path.exists(performance_file_name):
                with open("dao_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'rb') as infile:
                    prior_performance = pickle.load(infile)
                with open("dao_consensus_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as infile:
                    prior_consensus = pickle.load(infile)
                with open("dao_diversity_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as infile:
                    prior_diversity = pickle.load(infile)
                with open("dao_variance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as infile:
                    prior_variance = pickle.load(infile)
                performance_final = [(each_1 + each_2) / 2 for each_1, each_2 in zip(prior_performance, performance_final)]
                consensus_final = [(each_1 + each_2) / 2 for each_1, each_2 in zip(prior_consensus, consensus_final)]
                diversity_final = [(each_1 + each_2) / 2 for each_1, each_2 in zip(prior_diversity, diversity_final)]
                variance_final = [(each_1 + each_2) / 2 for each_1, each_2 in zip(prior_variance, variance_final)]
                with open("dao_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as out_file:
                    pickle.dump(performance_final, out_file)
                with open("dao_consensus_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as out_file:
                    pickle.dump(consensus_final, out_file)
                with open("dao_diversity_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as out_file:
                    pickle.dump(diversity_final, out_file)
                with open("dao_variance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as out_file:
                    pickle.dump(variance_final, out_file)

            else:
                with open("dao_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as out_file:
                    pickle.dump(performance_final, out_file)
                with open("dao_consensus_performance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as out_file:
                    pickle.dump(consensus_final, out_file)
                with open("dao_diversity_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as out_file:
                    pickle.dump(diversity_final, out_file)
                with open("dao_variance_incentive_{0}_inactive_{1}".format(incentive, active_rate), 'wb') as out_file:
                    pickle.dump(variance_final, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
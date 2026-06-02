# -*- coding: utf-8 -*-
# @Time     : 6/2/2026
# @Author   : Junyi
# @FileName: strategic_dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
"""
Run DAO experiments with strategic voting under equal token holdings.

This script is adapted from quadratic_dao_run.py. The key experimental
purpose is to test whether strategic voting reproduces its core intuition:
individuals increasingly align their expressed votes with the currently
perceived majority position, thereby strengthening coordination and reducing
expressed disagreement.

Important design note:
- The script keeps the same assign_tokens function used in the quadratic
  voting experiment.
- asymmetry = 0 means no token asymmetry. Every individual receives one token
  before the simulation starts.
- strategic_rate controls the probability that an individual aligns their vote
  with the currently perceived majority position rather than voting sincerely
  according to their own belief.
- strategic_rate = 0 corresponds to the sincere-voting baseline.
"""

import multiprocessing as mp
import pickle
import time
from multiprocessing import Semaphore

import numpy as np

from DAO_strategic import DAOStrategic
from Reality import Reality


def assign_tokens(dao=None, asymmetry=None, mode=10):
    """
    Assign token holdings to individuals.

    asymmetry = 0 gives everyone one token, corresponding to the no-asymmetry
    baseline. asymmetry > 0 gives Pareto-distributed token holdings.

    In the strategic-voting experiment below, asymmetry is configured as 0 so
    the experiment isolates the behavioral effect of strategic voting from
    token-concentration effects.
    """
    if asymmetry == 0:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = 1
    else:
        for team in dao.teams:
            for individual in team.individuals:
                individual.token = (np.random.pareto(a=asymmetry) + 1) * mode

    token_list = [
        individual.token
        for team in dao.teams
        for individual in team.individuals
    ]
    return token_list


def func(m=None, n=None, group_size=None, lr=None, asymmetry=None,
         strategic_rate=None, search_loop=None, loop=None, return_dict=None,
         sema=None, threshold_ratio=0.5, alpha=3):
    """Run one independent simulation repetition."""
    try:
        np.random.seed(None)

        reality = Reality(m=m, alpha=alpha)
        dao = DAOStrategic(m=m, n=n, reality=reality, lr=lr,
                           group_size=group_size, alpha=alpha)

        assign_tokens(dao=dao, asymmetry=asymmetry)

        for _ in range(search_loop):
            dao.search(threshold_ratio=threshold_ratio,
                       strategic_rate=strategic_rate)

        return_dict[loop] = {
            "performance": dao.performance_across_time,
            "consensus_performance": dao.consensus_performance_across_time,
            "diversity": dao.diversity_across_time,
            "variance": dao.variance_across_time,
            "entropy": dao.entropy_across_time,
            "antagonism": dao.antagonism_across_time,
            "switch_rate": dao.switch_rate_across_time,
        }
    finally:
        sema.release()


if __name__ == '__main__':
    t0 = time.time()

    m = 90
    n = 350
    lr = 0.3
    alpha = 3
    threshold_ratio = 0.5
    hyper_iteration = 10
    repetition = 100
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 100

    # Configure token holdings as the equal-token baseline.
    # asymmetry = 0 gives every individual one token.
    asymmetry = 0

    # strategic_rate = 0 is the sincere-voting baseline.
    # Larger values imply stronger strategic coordination around the perceived
    # majority position.
    strategic_rate_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    # After taking an average across repetitions.
    performance_across_para = []
    consensus_across_para = []
    diversity_across_para = []
    variance_across_para = []
    entropy_across_para = []
    antagonism_across_para = []
    switch_rate_across_para = []

    # Before taking an average across repetitions.
    performance_across_para_hyper = []
    consensus_across_para_hyper = []
    diversity_across_para_hyper = []
    variance_across_para_hyper = []
    entropy_across_para_hyper = []
    antagonism_across_para_hyper = []
    switch_rate_across_para_hyper = []

    for strategic_rate in strategic_rate_list:
        print("Strategic voting; strategic rate = {0}; {1}".format(
            strategic_rate,
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        ))

        performance_hyper = []
        consensus_hyper = []
        diversity_hyper = []
        variance_hyper = []
        entropy_hyper = []
        antagonism_hyper = []
        switch_rate_hyper = []

        for hyper_loop in range(hyper_iteration):
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []

            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(
                    target=func,
                    args=(m, n, group_size, lr, asymmetry, strategic_rate,
                          search_loop, loop, return_dict, sema,
                          threshold_ratio, alpha)
                )
                jobs.append(p)
                p.start()

            for proc in jobs:
                proc.join()

            results = list(return_dict.values())

            if len(results) != repetition:
                raise RuntimeError(
                    "Only {0} out of {1} repetitions returned results. "
                    "Please inspect child-process errors.".format(
                        len(results), repetition
                    )
                )

            performance_hyper += [result["performance"] for result in results]
            consensus_hyper += [
                result["consensus_performance"] for result in results
            ]
            diversity_hyper += [result["diversity"] for result in results]
            variance_hyper += [result["variance"] for result in results]
            entropy_hyper += [result["entropy"] for result in results]
            antagonism_hyper += [result["antagonism"] for result in results]
            switch_rate_hyper += [result["switch_rate"] for result in results]

        # Average trajectories across all repetitions and hyper-iterations.
        performance_across_para.append(
            np.mean(performance_hyper, axis=0).tolist()
        )
        consensus_across_para.append(
            np.mean(consensus_hyper, axis=0).tolist()
        )
        diversity_across_para.append(
            np.mean(diversity_hyper, axis=0).tolist()
        )
        variance_across_para.append(
            np.mean(variance_hyper, axis=0).tolist()
        )
        entropy_across_para.append(
            np.mean(entropy_hyper, axis=0).tolist()
        )
        antagonism_across_para.append(
            np.mean(antagonism_hyper, axis=0).tolist()
        )
        switch_rate_across_para.append(
            np.mean(switch_rate_hyper, axis=0).tolist()
        )

        # Preserve raw trajectories for robustness/statistical comparison.
        performance_across_para_hyper.append(performance_hyper)
        consensus_across_para_hyper.append(consensus_hyper)
        diversity_across_para_hyper.append(diversity_hyper)
        variance_across_para_hyper.append(variance_hyper)
        entropy_across_para_hyper.append(entropy_hyper)
        antagonism_across_para_hyper.append(antagonism_hyper)
        switch_rate_across_para_hyper.append(switch_rate_hyper)

    # Parameter list and token configuration.
    with open("dao_strategic_rate_list", 'wb') as out_file:
        pickle.dump(strategic_rate_list, out_file)
    with open("dao_strategic_asymmetry", 'wb') as out_file:
        pickle.dump(asymmetry, out_file)

    # After taking an average across repetitions.
    with open("dao_strategic_performance", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("dao_strategic_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para, out_file)
    with open("dao_strategic_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("dao_strategic_variance", 'wb') as out_file:
        pickle.dump(variance_across_para, out_file)
    with open("dao_strategic_entropy", 'wb') as out_file:
        pickle.dump(entropy_across_para, out_file)
    with open("dao_strategic_antagonism", 'wb') as out_file:
        pickle.dump(antagonism_across_para, out_file)
    with open("dao_strategic_switch_rate", 'wb') as out_file:
        pickle.dump(switch_rate_across_para, out_file)

    # Before taking an average across repetitions.
    with open("dao_strategic_original_performance", 'wb') as out_file:
        pickle.dump(performance_across_para_hyper, out_file)
    with open("dao_strategic_original_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para_hyper, out_file)
    with open("dao_strategic_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para_hyper, out_file)
    with open("dao_strategic_original_variance", 'wb') as out_file:
        pickle.dump(variance_across_para_hyper, out_file)
    with open("dao_strategic_original_entropy", 'wb') as out_file:
        pickle.dump(entropy_across_para_hyper, out_file)
    with open("dao_strategic_original_antagonism", 'wb') as out_file:
        pickle.dump(antagonism_across_para_hyper, out_file)
    with open("dao_strategic_original_switch_rate", 'wb') as out_file:
        pickle.dump(switch_rate_across_para_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

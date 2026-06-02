# -*- coding: utf-8 -*-
# @Time     : 5/23/2026
# @Author   : Junyi
# @FileName: quadratic_dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
"""
Run DAO experiments with quadratic voting under token asymmetry.

This script is adapted from dao_run.py. The key experimental purpose is to
test whether quadratic voting mitigates the negative effect of token asymmetry.

Important design note:
- asymmetry = 0 means no token asymmetry. Every individual receives one token.
  Under quadratic voting, sqrt(1) = 1, so this condition is equivalent to the
  one-person-one-vote baseline.
- asymmetry > 0 generates unequal token holdings from a Pareto distribution.
  In this parameterization, smaller positive Pareto shape values imply stronger
  token inequality.
- DAOQuadratic converts each individual's token holding into effective voting
  weight using sqrt(token), rather than token.
"""

import multiprocessing as mp
import pickle
import time
from multiprocessing import Semaphore

import numpy as np

from DAO_quadratic import DAOQuadratic
from Reality import Reality


def gini(array):
    """Calculate the Gini coefficient of a positive numeric array."""
    array = sorted(array)
    n = len(array)
    coefficient = 0
    for i, value in enumerate(array):
        coefficient += (2 * i + 1) * value
    coefficient /= n * sum(array)
    coefficient -= (n + 1) / n
    return coefficient


def assign_tokens(dao=None, asymmetry=None, mode=10):
    """
    Assign token holdings to individuals.

    asymmetry = 0 gives everyone one token, corresponding to the no-asymmetry
    baseline. asymmetry > 0 gives Pareto-distributed token holdings.
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
         search_loop=None, loop=None, return_dict=None, sema=None,
         threshold_ratio=0.5, alpha=3):
    """Run one independent simulation repetition."""
    try:
        np.random.seed(None)

        reality = Reality(m=m, alpha=alpha)
        dao = DAOQuadratic(m=m, n=n, reality=reality, lr=lr,
                           group_size=group_size, alpha=alpha)

        token_list = assign_tokens(dao=dao, asymmetry=asymmetry)
        gini_coef = gini(array=token_list)

        for _ in range(search_loop):
            dao.search(threshold_ratio=threshold_ratio)

        return_dict[loop] = {
            "performance": dao.performance_across_time,
            "consensus_performance": dao.consensus_performance_across_time,
            "diversity": dao.diversity_across_time,
            "variance": dao.variance_across_time,
            "gini": gini_coef,
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

    # asymmetry = 0 is the no-asymmetry / one-person-one-vote baseline.
    # For positive values, smaller asymmetry implies stronger token inequality.
    asymmetry_list = [0, 1, 2, 3]

    # After taking an average across repetitions.
    performance_across_para = []
    consensus_across_para = []
    diversity_across_para = []
    variance_across_para = []
    gini_across_para = []

    # Before taking an average across repetitions.
    performance_across_para_hyper = []
    consensus_across_para_hyper = []
    diversity_across_para_hyper = []
    variance_across_para_hyper = []
    gini_across_para_hyper = []

    for asymmetry in asymmetry_list:
        print("Quadratic voting; token asymmetry = {0}; {1}".format(
            asymmetry,
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        ))

        performance_hyper = []
        consensus_hyper = []
        diversity_hyper = []
        variance_hyper = []
        gini_hyper = []

        for hyper_loop in range(hyper_iteration):
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []

            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(
                    target=func,
                    args=(m, n, group_size, lr, asymmetry, search_loop,
                          loop, return_dict, sema, threshold_ratio, alpha)
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
            gini_hyper += [result["gini"] for result in results]

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
        gini_across_para.append(float(np.mean(gini_hyper)))

        # Preserve raw trajectories for robustness/statistical comparison.
        performance_across_para_hyper.append(performance_hyper)
        consensus_across_para_hyper.append(consensus_hyper)
        diversity_across_para_hyper.append(diversity_hyper)
        variance_across_para_hyper.append(variance_hyper)
        gini_across_para_hyper.append(gini_hyper)

    # Parameter list and Gini diagnostics.
    with open("dao_quadratic_asymmetry_list", 'wb') as out_file:
        pickle.dump(asymmetry_list, out_file)
    with open("dao_quadratic_gini", 'wb') as out_file:
        pickle.dump(gini_across_para, out_file)
    with open("dao_quadratic_original_gini", 'wb') as out_file:
        pickle.dump(gini_across_para_hyper, out_file)

    # After taking an average across repetitions.
    with open("dao_quadratic_performance", 'wb') as out_file:
        pickle.dump(performance_across_para, out_file)
    with open("dao_quadratic_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para, out_file)
    with open("dao_quadratic_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para, out_file)
    with open("dao_quadratic_variance", 'wb') as out_file:
        pickle.dump(variance_across_para, out_file)

    # Before taking an average across repetitions.
    with open("dao_quadratic_original_performance", 'wb') as out_file:
        pickle.dump(performance_across_para_hyper, out_file)
    with open("dao_quadratic_original_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_para_hyper, out_file)
    with open("dao_quadratic_original_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_para_hyper, out_file)
    with open("dao_quadratic_original_variance", 'wb') as out_file:
        pickle.dump(variance_across_para_hyper, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

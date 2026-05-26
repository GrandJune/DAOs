# -*- coding: utf-8 -*-
# @Time     : 5/18/2026
# @Author   : Junyi
# @FileName: hybrid_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import multiprocessing as mp
import pickle
import time
from multiprocessing import Semaphore

import numpy as np

from Hybrid import Hybrid
from Reality import Reality


def func(m=None, n=None, group_size=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, recentralization=None, return_dict=None,
         sema=None, alpha=3, p1=0.1, p2=0.9, token=False):
    """Run one independent simulation repetition.

    recentralization is passed to Hybrid as beta, because the revised
    Hybrid class defines beta as the degree of re-centralization.
    """
    try:
        np.random.seed(None)
        reality = Reality(m=m, alpha=alpha)
        hybrid = Hybrid(m=m, n=n, reality=reality, lr=lr, alpha=alpha,
                        group_size=group_size, beta=recentralization,
                        p1=p1, p2=p2)

        for _ in range(search_loop):
            hybrid.search(threshold_ratio=threshold_ratio, token=token)

        return_dict[loop] = {
            "performance": hybrid.performance_across_time,
            "diversity": hybrid.diversity_across_time,
            "variance": hybrid.variance_across_time,
            "cv": hybrid.cv_across_time,
            "entropy": hybrid.entropy_across_time,
            "antagonism": hybrid.antagonism_across_time,
            "consensus_performance": hybrid.consensus_performance_across_time,
            "mode": hybrid.mode_across_time,
        }
    finally:
        sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    alpha = 3
    p1 = 0.1
    p2 = 0.9
    threshold_ratio = 0.5
    hyper_iteration = 5
    repetition = 100
    concurrency = 100
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    token = False
    recentralization_list = np.arange(0, 1.01, 0.05).tolist()

    performance_recentralization = []
    diversity_recentralization = []
    variance_recentralization = []
    cv_recentralization = []
    entropy_recentralization = []
    antagonism_recentralization = []
    consensus_recentralization = []
    mode_recentralization = []

    for recentralization in recentralization_list:
        print("Re-centralization", recentralization,
              time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))

        performance_hyper = []
        diversity_hyper = []
        variance_hyper = []
        cv_hyper = []
        entropy_hyper = []
        antagonism_hyper = []
        consensus_hyper = []
        mode_hyper = []

        for hyper_loop in range(hyper_iteration):
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            jobs = []
            return_dict = manager.dict()

            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(
                    target=func,
                    args=(m, n, group_size, lr, threshold_ratio, search_loop,
                          loop, recentralization, return_dict, sema,
                          alpha, p1, p2, token)
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
            diversity_hyper += [result["diversity"] for result in results]
            variance_hyper += [result["variance"] for result in results]
            cv_hyper += [result["cv"] for result in results]
            entropy_hyper += [result["entropy"] for result in results]
            antagonism_hyper += [result["antagonism"] for result in results]
            consensus_hyper += [result["consensus_performance"] for result in results]
            mode_hyper += [result["mode"] for result in results]

        # Convert lists of lists to re-centralization-level average
        # trajectories.
        performance_recentralization.append(
            np.mean(performance_hyper, axis=0).tolist())
        diversity_recentralization.append(
            np.mean(diversity_hyper, axis=0).tolist())
        variance_recentralization.append(
            np.mean(variance_hyper, axis=0).tolist())
        cv_recentralization.append(np.mean(cv_hyper, axis=0).tolist())
        entropy_recentralization.append(
            np.mean(entropy_hyper, axis=0).tolist())
        antagonism_recentralization.append(
            np.mean(antagonism_hyper, axis=0).tolist())
        consensus_recentralization.append(
            np.mean(consensus_hyper, axis=0).tolist())

        # This diagnostic is not averaged numerically. It preserves raw mode
        # sequences across all repetitions and hyper-iterations for each
        # re-centralization level.
        mode_recentralization.append(mode_hyper)

    with open("hybrid_recentralization_list", 'wb') as out_file:
        pickle.dump(recentralization_list, out_file)
    with open("hybrid_performance", 'wb') as out_file:
        pickle.dump(performance_recentralization, out_file)
    with open("hybrid_diversity", 'wb') as out_file:
        pickle.dump(diversity_recentralization, out_file)
    with open("hybrid_variance", 'wb') as out_file:
        pickle.dump(variance_recentralization, out_file)
    with open("hybrid_cv", 'wb') as out_file:
        pickle.dump(cv_recentralization, out_file)
    with open("hybrid_entropy", 'wb') as out_file:
        pickle.dump(entropy_recentralization, out_file)
    with open("hybrid_antagonism", 'wb') as out_file:
        pickle.dump(antagonism_recentralization, out_file)
    with open("hybrid_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_recentralization, out_file)
    with open("hybrid_mode", 'wb') as out_file:
        pickle.dump(mode_recentralization, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Hybrid",
          time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))

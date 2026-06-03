# -*- coding: utf-8 -*-
# @Time     : 5/26/2026
# @Author   : Junyi
# @FileName: delegation_run.py
# Observing PEP 8 coding style

import multiprocessing as mp
import pickle
import time
from multiprocessing import Semaphore

import numpy as np

from Delegation import Delegation
from Reality import Reality


def func(m=None, n=None, group_size=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, delegation_rate=None,
         similarity_threshold=None, return_dict=None, sema=None, alpha=3,
         token=False, delegation_mode="random"):
    """Run one independent simulation repetition."""
    try:
        np.random.seed(None)

        reality = Reality(m=m, alpha=alpha)

        dao = Delegation(
            m=m,
            n=n,
            reality=reality,
            lr=lr,
            alpha=alpha,
            group_size=group_size,
            delegation_rate=delegation_rate,
            similarity_threshold=similarity_threshold
        )

        for _ in range(search_loop):
            dao.search(
                threshold_ratio=threshold_ratio,
                token=token,
                delegation_mode=delegation_mode,
                similarity_threshold=similarity_threshold
            )

        return_dict[loop] = {
            "performance": dao.performance_across_time,
            "diversity": dao.diversity_across_time,
            "variance": dao.variance_across_time,
            "consensus_performance": dao.consensus_performance_across_time,
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

    hyper_iteration = 5
    repetition = 100
    concurrency = 100
    search_loop = 300

    group_size = 7
    token = False

    # "random" or "performance" or "similarity"
    delegation_mode = "similarity"
    similarity_threshold = 0.5

    # focal parameter
    delegation_rate_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    performance_across_rate = []
    diversity_across_rate = []
    variance_across_rate = []
    consensus_across_rate = []

    for delegation_rate in delegation_rate_list:
        print(
            "Delegation Rate:",
            delegation_rate,
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        )

        performance_hyper = []
        diversity_hyper = []
        variance_hyper = []
        consensus_hyper = []

        for hyper_loop in range(hyper_iteration):
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            jobs = []
            return_dict = manager.dict()

            for loop in range(repetition):
                sema.acquire()

                p = mp.Process(
                    target=func,
                    args=(
                        m,
                        n,
                        group_size,
                        lr,
                        threshold_ratio,
                        search_loop,
                        loop,
                        delegation_rate,
                        similarity_threshold,
                        return_dict,
                        sema,
                        alpha,
                        token,
                        delegation_mode,
                    )
                )

                jobs.append(p)
                p.start()

            for proc in jobs:
                proc.join()

            results = list(return_dict.values())

            if len(results) != repetition:
                raise RuntimeError(
                    "Only {0} out of {1} repetitions returned results."
                    .format(len(results), repetition)
                )

            performance_hyper += [result["performance"] for result in results]
            diversity_hyper += [result["diversity"] for result in results]
            variance_hyper += [result["variance"] for result in results]
            consensus_hyper += [result["consensus_performance"] for result in results]

        performance_across_rate.append(np.mean(performance_hyper, axis=0).tolist())
        diversity_across_rate.append(np.mean(diversity_hyper, axis=0).tolist())
        variance_across_rate.append(np.mean(variance_hyper, axis=0).tolist())
        consensus_across_rate.append(np.mean(consensus_hyper, axis=0).tolist())

    output_prefix = delegation_mode + "_delegation"

    with open(output_prefix + "_rate_list", 'wb') as out_file:
        pickle.dump(delegation_rate_list, out_file)

    with open(output_prefix + "_performance", 'wb') as out_file:
        pickle.dump(performance_across_rate, out_file)

    with open(output_prefix + "_diversity", 'wb') as out_file:
        pickle.dump(diversity_across_rate, out_file)

    with open(output_prefix + "_variance", 'wb') as out_file:
        pickle.dump(variance_across_rate, out_file)

    with open(output_prefix + "_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_across_rate, out_file)

    t1 = time.time()

    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
    print(
        "Delegation:",
        delegation_mode,
        time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    )

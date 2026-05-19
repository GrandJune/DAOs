# -*- coding: utf-8 -*-
# @Time     : 5/18/2026
# @Author   : Junyi
# @FileName: hybrid_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Hybrid import Hybrid
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle


def func(m=None, n=None, group_size=None, lr=None, threshold_ratio=None,
         search_loop=None, loop=None, beta=None, return_dict=None,
         sema=None, alpha=3, p1=0.1, p2=0.9, token=False):
    np.random.seed(None)
    reality = Reality(m=m, alpha=alpha)
    hybrid = Hybrid(m=m, n=n, reality=reality, lr=lr, alpha=alpha,
                    group_size=group_size, beta=beta, p1=p1, p2=p2)
    for _ in range(search_loop):
        hybrid.search(threshold_ratio=threshold_ratio, token=token)

    return_dict[loop] = [
        hybrid.performance_across_time,
        hybrid.hybrid_code_performance_across_time,
        hybrid.diversity_across_time,
        hybrid.variance_across_time,
        hybrid.cv_across_time,
        hybrid.consensus_performance_across_time,
        hybrid.superior_performance_across_time,
        hybrid.mode_across_time,
    ]
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
    hyper_iteration = 10
    repetition = 50
    concurrency = 50
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    token = False
    beta_list = np.arange(0, 1.01, 0.1).round(1).tolist()

    performance_beta = []
    hybrid_code_beta = []
    diversity_beta = []
    variance_beta = []
    cv_beta = []
    consensus_beta = []
    superior_beta = []
    mode_beta = []

    for beta in beta_list:
        print("Beta", beta, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))

        performance_hyper = []
        hybrid_code_hyper = []
        diversity_hyper = []
        variance_hyper = []
        cv_hyper = []
        consensus_hyper = []
        superior_hyper = []
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
                          loop, beta, return_dict, sema, alpha, p1, p2, token)
                )
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()

            results = return_dict.values()  # Don't need dict index, since it is repetition.
            performance_hyper += [result[0] for result in results]
            hybrid_code_hyper += [result[1] for result in results]
            diversity_hyper += [result[2] for result in results]
            variance_hyper += [result[3] for result in results]
            cv_hyper += [result[4] for result in results]
            consensus_hyper += [result[5] for result in results]
            superior_hyper += [result[6] for result in results]
            mode_hyper += [result[7] for result in results]

        # Convert lists of lists to NumPy arrays
        performance_beta.append(np.mean(performance_hyper, axis=0).tolist())
        hybrid_code_beta.append(np.mean(hybrid_code_hyper, axis=0).tolist())
        diversity_beta.append(np.mean(diversity_hyper, axis=0).tolist())
        variance_beta.append(np.mean(variance_hyper, axis=0).tolist())
        cv_beta.append(np.mean(cv_hyper, axis=0).tolist())
        consensus_beta.append(np.mean(consensus_hyper, axis=0).tolist())
        superior_beta.append(np.mean(superior_hyper, axis=0).tolist())

        # This diagnostic is not averaged numerically. It preserves raw mode sequences
        # across all repetitions and hyper-iterations for each beta.
        mode_beta.append(mode_hyper)

    with open("hybrid_beta_list", 'wb') as out_file:
        pickle.dump(beta_list, out_file)
    with open("hybrid_performance", 'wb') as out_file:
        pickle.dump(performance_beta, out_file)
    with open("hybrid_code_performance", 'wb') as out_file:
        pickle.dump(hybrid_code_beta, out_file)
    with open("hybrid_diversity", 'wb') as out_file:
        pickle.dump(diversity_beta, out_file)
    with open("hybrid_variance", 'wb') as out_file:
        pickle.dump(variance_beta, out_file)
    with open("hybrid_cv", 'wb') as out_file:
        pickle.dump(cv_beta, out_file)
    with open("hybrid_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_beta, out_file)
    with open("hybrid_superior_performance", 'wb') as out_file:
        pickle.dump(superior_beta, out_file)
    with open("hybrid_mode", 'wb') as out_file:
        pickle.dump(mode_beta, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Hybrid", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))  # Complete time

# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from DAO import DAO
from Hierarchy import Hierarchy
from Autonomy import Autonomy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Pool
from multiprocessing import Semaphore
import pickle
import math


def func(loop=None, return_dict=None, sema=None):
    np.random.seed(None)

    m = 60 # policy_num = 20; every 50 iterations form a consensus -> need 1k iterations
    n = 280
    search_loop = 300
    lr = 0.3
    group_size = 7  # the smallest group size in Fang's model: 7
    reality = Reality(m=m, version="Rushed", alpha=3)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, alpha=3)

    for period in range(search_loop):
        dao.interrupted_search(threshold_ratio=0.5, current_iteration=period)

    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time, dao.cv_across_time, dao.entropy_across_time, dao.antagonism_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    threshold_ratio = 0.5
    hyper_iteration = 10
    repetition = 50
    concurrency = 50
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    performance_hyper = []
    consensus_hyper = []
    diversity_hyper = []
    variance_hyper = []
    cv_hyper = []
    entropy_hyper = []
    antagonism_hyper = []
    for hyper_loop in range(hyper_iteration):
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_hyper += [result[0] for result in results]
        consensus_hyper += [result[1] for result in results]
        diversity_hyper += [result[2] for result in results]
        variance_hyper += [result[3] for result in results]
        cv_hyper += [result[4] for result in results]
        entropy_hyper += [result[5] for result in results]
        antagonism_hyper += [result[6] for result in results]

    performance_final = list(np.mean(performance_hyper, axis=0))
    consensus_final = list(np.mean(consensus_hyper, axis=0))
    diversity_final = list(np.mean(diversity_hyper, axis=0))
    variance_final = list(np.mean(variance_hyper, axis=0))
    cv_final = list(np.mean(cv_hyper, axis=0))
    entropy_final = list(np.mean(entropy_hyper, axis=0))
    antagonism_final = list(np.mean(antagonism_hyper, axis=0))


    with open("dao_performance", 'wb') as out_file:
        pickle.dump(performance_final, out_file)
    with open("dao_consensus_performance", 'wb') as out_file:
        pickle.dump(consensus_final, out_file)
    with open("dao_diversity", 'wb') as out_file:
        pickle.dump(diversity_final, out_file)
    with open("dao_variance", 'wb') as out_file:
        pickle.dump(variance_final, out_file)
    with open("dao_cv", 'wb') as out_file:
        pickle.dump(cv_final, out_file)
    with open("dao_entropy", 'wb') as out_file:
        pickle.dump(entropy_final, out_file)
    with open("dao_antagonism", 'wb') as out_file:
        pickle.dump(antagonism_final, out_file)

    import matplotlib.pyplot as plt
    x = range(search_loop)
    plt.plot(x, performance_final, "k-", label="Mean")
    plt.plot(x, consensus_final, "k--", label="Consensus")
    # plt.title('Performance')
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_performance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Diversity
    plt.plot(x, diversity_final, "k-", label="DAO")
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Diversity', fontweight='bold', fontsize=10)
    # plt.title('Diversity')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_diversity.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Variance
    plt.plot(x, variance_final, "k-", label="DAO")
    # Add shaded gray area for 10 iterations every 50 iterations
    for i in range(0, max(x) + 1, 50):
        plt.axvspan(i, i + 10, color='gray', alpha=0.2)  # adjust alpha for visibility

        # Optional: Add dashed lines at the start of each interval
        plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
        # Dashed line at the end
        plt.axvline(x=i + 10, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Variance', fontweight='bold', fontsize=10)
    # plt.title('Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Coefficient of Variance
    plt.plot(x, cv_final, "k-", label="DAO")
    # Add shaded gray area for 10 iterations every 50 iterations
    for i in range(0, max(x) + 1, 50):
        plt.axvspan(i, i + 10, color='gray', alpha=0.2)  # adjust alpha for visibility

        # Optional: Add dashed lines at the start of each interval
        plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
        # Dashed line at the end
        plt.axvline(x=i + 10, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Coefficient of Variance', fontweight='bold', fontsize=10)
    # plt.title('Coefficient of Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_coefficient_of_variance.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    # Entropy
    plt.plot(x, entropy_final, "k-", label="DAO")
    # Add shaded gray area for 10 iterations every 50 iterations
    for i in range(0, max(x) + 1, 50):
        plt.axvspan(i, i + 10, color='gray', alpha=0.2)  # adjust alpha for visibility

        # Optional: Add dashed lines at the start of each interval
        plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
        # Dashed line at the end
        plt.axvline(x=i + 10, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Shannon Entropy', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_entropy.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()


    # Antagonism
    plt.plot(x, antagonism_final, "k-", label="DAO")
    # Add shaded gray area for 10 iterations every 50 iterations
    for i in range(0, max(x) + 1, 50):
        plt.axvspan(i, i + 10, color='gray', alpha=0.2)  # adjust alpha for visibility

        # Optional: Add dashed lines at the start of each interval
        plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
        # Dashed line at the end
        plt.axvline(x=i + 10, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Antagonism Index', fontweight='bold', fontsize=10)
    # plt.title('Coefficient of Variance')
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("DAO_antagonism.png", transparent=False, dpi=1200)
    plt.show()
    plt.clf()

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


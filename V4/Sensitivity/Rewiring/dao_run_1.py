# -*- coding: utf-8 -*-
# @Time     : 10/9/2022 22:52
# @Author   : Junyi
# @FileName: dao_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from RewiringDAO import DAO
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle


def func(m=None, n=None, group_size=None, lr=None, threshold_ratio=None, beta=None,
         search_loop=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m)
    dao = DAO(m=m, n=n, reality=reality, lr=lr, group_size=group_size, beta=beta)
    for _ in range(search_loop):
        dao.search(threshold_ratio=threshold_ratio)
    return_dict[loop] = [dao.performance_across_time, dao.consensus_performance_across_time,
                         dao.diversity_across_time, dao.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    n = 350
    lr = 0.3
    threshold_ratio = 0.5
    repetition = 400
    concurrency = 50
    search_loop = 300
    group_size = 7  # the smallest group size in Fang's model: 7
    beta_list = [0.1, 0.2, 0.3]
    for beta in beta_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(m, n, group_size, lr, threshold_ratio, beta, search_loop, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        performance_across_time_repeat = [result[0] for result in results]
        consensus_across_time_repeat = [result[1] for result in results]
        diversity_across_time_repeat = [result[2] for result in results]
        variance_across_time_repeat = [result[3] for result in results]

        performance_final = []
        consensus_final = []
        diversity_final = []
        variance_final = []
        for period in range(search_loop):
            temp_performance = [rss_list[period] for rss_list in performance_across_time_repeat]
            temp_consensus = [rss_list[period] for rss_list in consensus_across_time_repeat]
            temp_diversity = [rss_list[period] for rss_list in diversity_across_time_repeat]
            temp_variance = [rss_list[period] for rss_list in variance_across_time_repeat]

            performance_final.append(sum(temp_performance) / len(temp_performance))
            consensus_final.append(sum(temp_consensus) / len(temp_consensus))
            diversity_final.append(sum(temp_diversity) / len(temp_diversity))
            variance_final.append(sum(temp_variance) / len(temp_variance))

        with open("dao_performance_beta_{0}".format(beta), 'wb') as out_file:
            pickle.dump(performance_final, out_file)
        with open("dao_consensus_performance_beta_{0}".format(beta), 'wb') as out_file:
            pickle.dump(consensus_final, out_file)
        with open("dao_diversity_beta_{0}".format(beta), 'wb') as out_file:
            pickle.dump(diversity_final, out_file)
        with open("dao_variance_beta_{0}".format(beta), 'wb') as out_file:
            pickle.dump(variance_final, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


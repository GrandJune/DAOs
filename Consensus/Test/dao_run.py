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


def func(m=None, s=None, n=None, group_size=None, lr=None, asymmetry=None,
         search_loop=None, sema=None):
    np.random.seed(None)
    reality = Reality(m=m, s=s)
    dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr, subgroup_size=group_size)
    # pre-assign the token according to the asymmetry degree
    if asymmetry == 0:
        for individual in dao.individuals:
            individual.token = 1
    else:
        for individual in dao.individuals:
            individual.token = np.random.pareto(a=asymmetry)
    for period in range(search_loop):
        dao.search(threshold_ratio=0.6, enable_token=True)
    print("Code: ", reality.real_code, "Payoff: ", dao.individuals[0].payoff, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
    print("CPU的核数为：{}".format(mp.cpu_count()))
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 30
    s = 1
    n = 70
    lr = 0.3
    hyper_iteration = 1
    repetition = 100
    search_loop = 100
    group_size = 7  # the smallest group size in Fang's model: 7
    concurrency = 100
    asymmetry_list = [0]  # smaller asymmetry is associated with higher wealth inequality
    # after taking an average across repetitions
    performance_across_para = []
    consensus_across_para = []
    diversity_across_para = []
    # before taking an average across repetitions
    performance_across_para_hyper = []
    consensus_across_para_hyper = []
    diversity_across_para_hyper = []
    for asymmetry in asymmetry_list:
        # after taking an average across repetitions
        performance_final = []
        consensus_final = []
        diversity_final = []
        # before taking an average across repetitions
        performance_hyper = []
        consensus_hyper = []
        diversity_hyper = []
        for hyper_loop in range(hyper_iteration):
            sema = Semaphore(concurrency)
            manager = mp.Manager()
            return_dict = manager.dict()
            jobs = []
            for loop in range(repetition):
                sema.acquire()
                p = mp.Process(target=func,
                               args=(m, s, n, group_size, lr, asymmetry, search_loop, sema))
                jobs.append(p)
                p.start()
            for proc in jobs:
                proc.join()
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))

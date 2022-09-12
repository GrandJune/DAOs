# -*- coding: utf-8 -*-
# @Time     : 9/3/2022 14:51
# @Author   : Junyi
# @FileName: dao_s.py
# @Software  : PyCharm
# Observing PEP 8 coding style
# Comparison between Overall Payoff, Policy Payoff, and Belief Payoff
from Superior import Superior
from Superior_2 import Superior_2
from Reality import Reality
from Individual import Individual
import matplotlib.pyplot as plt
import numpy as np
import time
import multiprocessing as mp
import pickle


def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version=None, loop=None, return_dict=None):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=1.0)
    data_across_time = []
    for _ in range(search_round):
        superior.weighted_local_search()
        payoff_list = [individual.payoff for individual in superior.individuals]
        data_across_time.append(sum(payoff_list) / len(payoff_list))
    return_dict[loop] = data_across_time

def func_2(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version=None, loop=None, return_dict=None):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior_2(m=m, s=s, t=t, n=n, reality=reality, authority=1.0)
    data_across_time = []
    for _ in range(search_round):
        superior.weighted_local_search()
        payoff_list = [individual.payoff for individual in superior.individuals]
        data_across_time.append(sum(payoff_list) / len(payoff_list))
    return_dict[loop] = data_across_time

if __name__ == '__main__':
    t0 = time.time()
    m = 36
    s = 3
    t = 3
    n = 100
    data_across_para = []
    version = "Weighted"
    repetition_round = 100
    search_round = 300
    authority = 1.0
    # Short search
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition_round):
        p = mp.Process(target=func, args=(m, s, t, authority, n, search_round, version, loop, return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    data_across_repetition = return_dict.values()
    result_1 = []
    for i in range(search_round):
        temp = [payoff_list[i] for payoff_list in data_across_repetition]
        result_1.append(sum(temp) / len(temp))

    # Long search
    manager = None
    return_dict = None
    manager = mp.Manager()
    return_dict = manager.dict()
    jobs = []
    for loop in range(repetition_round):
        p = mp.Process(target=func_2, args=(m, s, t, authority, n, search_round, version, loop, return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    data_across_repetition = return_dict.values()
    result_2 = []
    for i in range(search_round):
        temp = [payoff_list[i] for payoff_list in data_across_repetition]
        result_2.append(sum(temp) / len(temp))

    x = range(search_round)
    plt.plot(x, result_1, "b--", label="Short")
    plt.plot(x, result_2, "g:", label="Long")
    plt.title('Long versus Short Hierarchy Search')
    plt.xlabel('Iteration')
    plt.ylabel('Performance')
    plt.legend()
    plt.savefig("Long_Short_Hierarchy.png")
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
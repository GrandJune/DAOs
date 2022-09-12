from Superior import Superior
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
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=1.0)
    data_across_time = []
    for _ in range(search_round):
        superior.random_guess()
        payoff_list = [individual.payoff for individual in superior.individuals]
        data_across_time.append(sum(payoff_list) / len(payoff_list))
    return_dict[loop] = data_across_time

if __name__ == '__main__':
    t0 = time.time()
    m = 100
    s = 5
    t = 5
    n = 100
    data_across_para = []
    version = "Weighted"
    repetition_round = 100
    search_round = 500
    authority = 1.0
    # Difficult Strategic Search
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

    # Random Guess
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
    plt.plot(x, result_1, "b--", label="Difficult")
    plt.plot(x, result_2, "g:", label="Random")
    plt.title('Difficult versus Random Hierarchy Search')
    plt.xlabel('Iteration')
    plt.ylabel('Performance')
    plt.legend()
    plt.savefig("Difficult_Random_Hierarchy.png")
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
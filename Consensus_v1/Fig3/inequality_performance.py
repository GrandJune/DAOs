from Superior import Superior
from Reality import Reality
# import matplotlib
# matplotlib.use('agg')  # For NUS HPC only
# import matplotlib.pyplot as plt
import pickle
import time
import numpy as np
import multiprocessing as mp


def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version="Rushed", loop=None, asymmetry=None, return_dict_1=None, return_dict_2=None):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    # Assign the token or decision power
    for individual in superior.individuals:
        individual.token = np.random.pareto(a=asymmetry)
    consensus = [0] * (m // s)
    performance_across_time = []
    diversity_across_time = []
    for _ in range(search_round):
        diversity_across_time.append(superior.get_diversity())
        for individual in superior.individuals:
            next_index = np.random.choice(len(consensus))
            next_policy = consensus[next_index]
            individual.constrained_local_search_under_consensus(focal_policy=next_policy, focal_policy_index=next_index)
        consensus = []
        for i in range(m//s):
            temp = sum(individual.policy[i] * individual.token for individual in superior.individuals)
            if temp < 0:
                consensus.append(-1)
            elif temp > 0:
                consensus.append(1)
            else:
                consensus.append(0)
        performance_list = [individual.payoff for individual in superior.individuals]
        performance_across_time.append(sum(performance_list) / len(performance_list))
    return_dict_1[loop] = performance_across_time
    return_dict_2[loop] = diversity_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 60
    s = 3
    t = 1
    n = 100
    search_round = 600
    repetition_round = 200
    version = "Rushed"
    authority = False  # !!!!!!!!!!!!!!!! Without authority !!!!!!!!!!!!!!!!!!
    asymmetry_list = [1, 2, 4, 8]  # small asymmetry is associated with high wealth inequality
    data_1_across_para, data_2_across_para = [], []
    for asymmetry in asymmetry_list:
        manager = mp.Manager()
        return_dict_1 = manager.dict()
        return_dict_2 = manager.dict()
        jobs = []
        for loop in range(repetition_round):
            p = mp.Process(target=func, args=(m, s, t, authority, n, search_round, version, loop,asymmetry, return_dict_1, return_dict_2))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        performance_across_repetition = return_dict_1.values()
        diversity_across_repetition = return_dict_2.values()

        result_1 = []
        for i in range(search_round):
            temp = [payoff_list[i] for payoff_list in performance_across_repetition]
            result_1.append(sum(temp) / len(temp))
        data_1_across_para.append(result_1)

        result_2 = []
        for i in range(search_round):
            temp = [diversity_list[i] for diversity_list in diversity_across_repetition]
            result_2.append(sum(temp) / len(temp))
        data_2_across_para.append(result_2)
    # Save the original data for further analysis
    with open("dao_performance_across_asymmetry", 'wb') as out_file:
        pickle.dump(data_1_across_para, out_file)
    with open("dao_diversity_across_asymmetry", 'wb') as out_file:
        pickle.dump(data_2_across_para, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))
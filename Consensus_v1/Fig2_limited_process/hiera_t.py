# -*- coding: utf-8 -*-
# @Time     : 8/5/2022 20:22
# @Author   : Junyi
# @FileName: hs.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Superior import Superior
from Reality import Reality
# import matplotlib
# matplotlib.use('agg')  # For NUS HPC only
# import matplotlib.pyplot as plt
import pickle
import time
import multiprocessing as mp
from multiprocessing import Pool


# multiprocessing
# def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
#          version="Rushed", loop=None, return_dict=None):
#     reality = Reality(m=m, s=s, t=t, version=version)
#     superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
#     diversity_across_time = []
#     for _ in range(search_round):
#         diversity_across_time.append(superior.get_diversity())
#         superior.local_search()
#     return_dict[loop] = diversity_across_time
#
#
# if __name__ == '__main__':
#     t0 = time.time()
#     m = 60
#     s = 3
#     t_list = [1, 2, 3, 4, 5]
#     n = 100
#     search_round = 300
#     repetition_round = 100
#     version = "Rushed"
#     authority = 1.0  # !!!!!!!!!!!!!!!! With authority !!!!!!!!!!!!!!!!!!
#     data_across_para = []
#     for t in t_list:
#         m = 90
#         m = s * t * (m // (s * t))
#         manager = mp.Manager()
#         return_dict = manager.dict()
#         jobs = []
#         for loop in range(repetition_round):
#             p = mp.Process(target=func, args=(m, s, t, authority, n, search_round, version, loop, return_dict))
#             jobs.append(p)
#             p.start()
#
#         for proc in jobs:
#             proc.join()
#         diversity_across_repetition = return_dict.values()
#
#         result_1 = []
#         for i in range(search_round):
#             temp = [diversity_list[i] for diversity_list in diversity_across_repetition]
#             result_1.append(sum(temp) / len(temp))
#         data_across_para.append(result_1)
#     # Save the original data for further analysis
#     with open("hierarchy_diversity_across_t", 'wb') as out_file:
#         pickle.dump(data_across_para, out_file)
#     t1 = time.time()
#     print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


# 有限线程
def func(m=None, s=None, t=None, authority=None, n=None, search_round=None,
         version="Rushed"):
    reality = Reality(m=m, s=s, t=t, version=version)
    superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=authority)
    diversity_across_time = []
    for _ in range(search_round):
        diversity_across_time.append(superior.get_diversity())
        superior.local_search()
    return diversity_across_time


if __name__ == '__main__':
    t0 = time.time()
    m = 60
    s = 3
    t_list = [1, 2, 3, 4, 5]
    n = 100
    search_round = 300
    repetition_round = 100
    version = "Rushed"
    authority = 1.0  # !!!!!!!!!!!!!!!! With authority !!!!!!!!!!!!!!!!!!
    data_across_para = []
    for t in t_list:
        m = 60
        m = s * t * (m // (s * t))
        cpu_num = mp.cpu_count()
        pool = Pool(cpu_num)
        diversity_across_repetition = []
        for i in range(repetition_round):
            diversity_across_repetition.append(pool.apply_async(func=func, args=((m, s, t, authority, n, search_round, version))).get())
        result_1 = []
        for i in range(search_round):
            temp = [diversity_list[i] for diversity_list in diversity_across_repetition]
            result_1.append(sum(temp) / len(temp))
        data_across_para.append(result_1)
    # Save the original data for further analysis
    with open("Hierarchy_diversity_t", 'wb') as out_file:
        pickle.dump(data_across_para, out_file)
    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

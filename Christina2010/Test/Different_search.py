# -*- coding: utf-8 -*-
# @Time     : 6/11/2022 15:58
# @Author   : Junyi
# @FileName: Different_search.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import time
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from Reality import Reality
from Individual import Individual
from Organization import Organization
import numpy as np
import pickle
import multiprocessing as mp


n = 280
beta = 0
# m = 100
# s = 1
lr = 0.3
subgroup_size = 7
reality_change_rate = 0
change_freq = None
loop = 1000


def func(flag=None, payoff_flag=None, m=None, s=None):
    t0 = time.time()
    reality = Reality(m=m, s=s)
    organization = Organization(n=n, beta=beta, subgroup_size=subgroup_size, m=m, s=s, reality=reality,
                                lr=lr, reality_change_rate=reality_change_rate)
    organization.form_network()
    # organization.individuals[0].describe()
    organization.process(loop=loop, change_freq=change_freq, flag=flag, payoff_flag=payoff_flag)
    # organization.describe()
    x = np.arange(loop)
    plt.plot(x, organization.performance_curve, "k-")
    t1 = time.time()
    plt.savefig("m{0}s{1}_{2}_t{3}.jpg".format(m, s, flag, t1 - t0))


if __name__ == '__main__':
    for m in [280]:
        for s in [1, 2, 5]:
            for flag in ["slim_search", "local_search"]:
                for payoff_flag in ["discrete", "bidirection"]:
                    p = mp.Process(target=func, args=(flag, payoff_flag, m, s))
                    p.start()
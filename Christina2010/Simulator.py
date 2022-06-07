# -*- coding: utf-8 -*-
# @Time     : 6/6/2022 19:19
# @Author   : Junyi
# @FileName: Simulator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np


class Simulator:
    def __init__(self, turnover=0, envir_change=0.1, learn=0.1, beta=0, subgroup_size=7, m=40, n=40, s=1, T=200):
        self.n = n  # Number of individuals in the organization
        self.m = m  # dimension of beliefs
        self.subgroup_size = subgroup_size  # z, size of the subgroup
        self.beta = beta  # the rewiring probability (reshaping the network)
        self.learn = learn  # Probability of individual learning from the majority view (organization code)
        self.s = s  # Degree of complexity
        self.turnover = turnover  # Probability of turnover
        self.envir_change = envir_change  # Probability of change in each element of reality
        self.T = T  # Interval for environment change

    def learning(self):
        pass
    def turnover(self):
        pass
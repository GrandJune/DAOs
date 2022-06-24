# -*- coding: utf-8 -*-
# @Time     : 6/22/2022 15:07
# @Author   : Junyi
# @FileName: Organization.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Reality import Reality
import numpy as np


class Organization:
    def __init__(self, m=None, s=None, reality=None):
        self.m = m
        self.s = s
        self.reality = reality
        self.code = np.random.choice([-1, 1], m, p=[0.5, 0.5])
        self.payoff = self.reality.get_payoff(belief=self.code)

    def assign_task(self):
        """
        Decisde on the task allocation via peer-to-peer voting
        :return:
        """
        pass

    def proposal(self):
        pass

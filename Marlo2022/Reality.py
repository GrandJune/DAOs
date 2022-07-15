# -*- coding: utf-8 -*-
# @Time     : 7/14/2022 20:44
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np


class Reality:
    def __init__(self, N=None, interdependency=None):
        self.N = N # task number
        self.interdependency = interdependency   # occurs in the extensive model

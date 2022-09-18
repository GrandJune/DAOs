# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import time
import numpy as np
import math


class Reality:
    def __init__(self, m=None, s=None, version="Rushed"):
        self.m = m
        self.s = s
        if self.s < 1:
            raise ValueError("The number of complexity should be greater than 0")
        if self.s > self.m:
            raise ValueError("The number of complexity should be less than the number of reality")
        self.version = version
        self.cell_num = math.ceil(m / s)
        self.real_code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])

    def get_payoff(self, belief=None):
        ress = 0
        if self.version == "Rushed":
            for i in range(self.cell_num):
                if np.array_equiv(belief[i*self.s: (i+1)*self.s], self.real_code[i*self.s: (i+1)*self.s]):
                    ress += 1
            ress = ress * self.s / self.m
        elif self.version == "Penalty":
            for i in range(self.cell_num):
                temp = 0
                for j in range(self.s):
                    temp += belief[i*self.s + j] * self.real_code[i*self.s + j]
                ress += temp
            ress /= self.m
        return ress

    def belief_2_policy(self, belief):
        policy = []
        for i in range(self.cell_num):
            temp = sum(belief[i * self.s:(i + 1) * self.s])
            if temp < 0:
                policy.append(-1)
            elif temp > 0:
                policy.append(1)
            else:
                policy.append(0)
        return policy


if __name__ == '__main__':
    m = 20
    s = 2
    t = 1
    version = "Rushed"
    reality = Reality(m, s, t, version=version)
    # belief = [1] * 6
    belief = reality.real_code.copy()
    belief[-1] *= -1
    t0 = time.time()
    for _ in range(100):
        payoff = reality.get_payoff(belief=belief)
        print(reality.real_code)
        print(belief)
        print(payoff)
    t1 = time.time()
    # print(t1-t0)
    # print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))


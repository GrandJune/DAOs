# -*- coding: utf-8 -*-
# @Time     : 6/9/2022 15:21
# @Author   : Junyi
# @FileName: Reality.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import math


class Reality:
    def __init__(self, m=10, s=1):
        self.m = m
        self.s = s
        if self.s < 1:
            raise ValueError("The number of complexity should be greater than 0")
        if self.s > self.m:
            raise ValueError("The number of complexity should be less than the number of reality")
        self.dependency_cell_num = math.ceil(m / s)
        self.real_code = np.random.choice([-1, 1], self.m, p=[0.5, 0.5])

    def describe(self):
        print("m: {0}, s: {1}, cells: {2}".format(self.m, self.s, self.dependency_cell_num))
        print("Reality Code: ", self.real_code)
        print("*"*10)

    def get_payoff(self, belief=None):
        """
        Calculate the payoff of the belief
        :param belief: either the individual belief or the organizational code
        :return: payoff
        """
        ress = 0
        for i in range(self.dependency_cell_num):
            correct_num = 0
            for j in range(self.s):
                index = i * self.s + j
                if index >= self.m:
                    break
                else:
                    if self.real_code[index] * belief[index] == 1:
                        correct_num += 1
            # A generalized payoff function for Christina's m/s payoff function
            # when correct_num = 0, and s, the payoff expectation would be 0 and s, respectively.
            # That's the Christina's model.
            # for correct_num varying from 1 to (s-1), the expectation would be (correct_num)^2/s
            ress += np.random.choice([0, correct_num], p=[1-correct_num / self.s, correct_num / self.s])
        return ress / self.m

    def get_partial_payoff(self, belief=None, task=None):
        """
        Calculate the payoff for a specific belief piece
        :param belief: belief piece
        :return: partial payoff
        """
        cell_index = [index // self.dependency_cell_num for index in range(self.m) if index in task]
        cell_index = set(cell_index)
        ress = 0
        for cell in cell_index:
            correct_num = 0
            for j in range(self.s):
                index = cell * self.s + j
                if index >= self.m:
                    break
                else:
                    if self.real_code[index] * belief[index] == 1:
                        correct_num += 1
            ress += np.random.choice([0, correct_num], p=[1-correct_num / self.s, correct_num / self.s])
        return ress / self.m

    def change(self, reality_change_rate=None):
        if reality_change_rate:
            for index in range(self.m):
                if np.random.uniform(0, 1) < reality_change_rate:
                    self.real_code[index] *= -1

    def generate_task(self, task_size=None):
        if not task_size:
            task_size = math.ceil(self.m * 0.5)
        task = np.random.choice(range(self.m), task_size, p=[1 / self.m] * self.m)
        return task


if __name__ == '__main__':
    m = 10
    s = 3
    reality = Reality(m=m, s=s)
    # reality.describe()
    result = reality.get_payoff(belief=[1]*m)
    reality.describe()
    print(result)

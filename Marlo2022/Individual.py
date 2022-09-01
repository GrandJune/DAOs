# -*- coding: utf-8 -*-
# @Time     : 7/14/2022 21:02
# @Author   : Junyi
# @FileName: Individual.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import matplotlib.pyplot as plt


class Individual:
    def __init__(self, skill_mean=None, skill_sigma=None, skill_num=None):
        self.skills = []
        for _ in range(skill_num):
            skill = np.random.normal(skill_mean, skill_sigma)
            self.skills.append(abs(skill))
            # if (skill > skill_mean - 3 * skill_sigma) and (skill < skill_mean + 3 * skill_sigma):
            #     self.skills.append(skill)
        self.skills = [i/sum(self.skills) for i in self.skills]  # normalize
        self.skill_gap = (max(self.skills) - min(self.skills)) / min(self.skills)


if __name__ == '__main__':
    skill_num = 50
    skill_mean = 1
    skill_sigma = 1
    sigma_list = np.arange(0.1, 0.9, 0.01)
    skill_gap_list = []
    for sigma in sigma_list:
        skill_gap = []
        for _ in range(100):
            individual = Individual(skill_mean, sigma, skill_num)
            skill_gap.append(individual.skill_gap)
        skill_gap = sum(skill_gap)/len(skill_gap)
        skill_gap_list.append(skill_gap)
    x = sigma_list
    plt.plot(x, skill_gap_list, "k-")
    # plt.savefig("search.jpg")
    plt.title('Skill Gap Across Sigma')
    plt.xlabel('Sigma')
    plt.ylabel('Skill Gap')
    plt.show()
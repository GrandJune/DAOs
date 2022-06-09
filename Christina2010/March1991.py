# -*- coding: utf-8 -*-
# @Time     : 6/3/2022 16:48
# @Author   : Junyi
# @FileName: Entities.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np

# March 1991's paper, as reference


class Reality:
    def __init__(self, element_num=10):
        self.element_num = element_num
        self.state = np.random.choice([-1, 1], self.element_num, p=[0.5, 0.5])

    def change_state(self,):
        self.state = np.random.choice([-1, 1], self.element_num, p=[0.5, 0.5])


class Individual:
    def __init__(self, element_num, p1):
        self.element_num = element_num
        self.belief = np.random.choice([-1, 0, 1], self.element_num, p=[1 / 3, 1 / 3, 1 / 3])
        # 0 refers to the unknown domain.
        # p1 refers to the socialization effectiveness, i.e., learning from the code
        self.socialization_rate = p1

    def socialization(self, code):
        """

        :param code:
        :return:
        """
        belief = list(self.belief)
        res = []
        if np.random.uniform(0, 1) < 0.5:
            learn_tag = True
        else:
            learn_tag = False

        if learn_tag:
            for cur in range(len(code)):
                if code[cur] == 0:
                    res.append(belief[cur])
                else:
                    # Learning from the code, or remain still
                    # with probability of p1, to learn from organization code (called as socialization)
                    if np.random.uniform(0, 1) < self.socialization_rate:
                        res.append(code[cur])
                    else:
                        res.append(belief[cur])
            self.belief = list(res)

    def volitional_socialization(self, code, peers, upper=0.1, lower=0.9):
        social_aspiration = np.mean([similarity_count(individual.belief, code) for individual in peers])
        focal_similarity = similarity_count(self.belief, code)

        learn_tag = False
        if focal_similarity > social_aspiration:
            if np.random.uniform(0, 1) < upper:
                learn_tag = True
        else:
            if np.random.uniform(0, 1) < lower:
                learn_tag = True
        if learn_tag:
            belief = list(self.belief)

            res = []

            for cur in range(len(code)):
                if code[cur] == 0:
                    res.append(belief[cur])
                else:
                    if np.random.uniform(0, 1) < self.socialization_rate:
                        res.append(code[cur])
                    else:
                        res.append(belief[cur])
            self.belief = list(res)


class Organization:

    def __init__(self, element_num, individuals, p2):
        self.element_num = element_num
        # organization code, each of the dimension is initially 0
        self.code = np.random.choice([0], self.element_num)
        # A list of individuals
        self.individuals = individuals
        # p2 refers to the learning effitiveness, i.e., learning by the code
        self.adaptation_rate = p2

    def calculate_k(self, superior_group):
        """
        Compare the organization code and the superior goup's belief
        SO what's k? -> the organizational knowledge
        :param superior_group: have a better similarity than the organizational code
        :return:
        """
        res = []
        for cur in range(self.element_num):
            k = 0
            for individual in superior_group:
                if individual.belief[cur] == self.code[cur]:
                    k -= 1
                else:
                    k += 1
            res.append(k)
        return res

    def turnover(self, p3):
        """
        Personnel Turnover
        :param p3: the probability of changing one individual
        :return: update the organizational individual list
        """
        individuals = list(self.individuals)
        socialization_rate = individuals[0].socialization_rate
        res = []
        for cur in range(len(individuals)):
            if np.random.uniform(0, 1) < p3:
                res.append(Individual(30, socialization_rate))
            else:
                res.append(individuals[cur])
        self.individuals = list(res)

    def adaptation(self, reality_code):
        """
        :param reality_code: from the external reality class, have a correct code as the search target
        :return:
        """
        organization_similarity = similarity_count(self.code, reality_code)
        superior_group = []
        for individual in self.individuals:
            individual_similarity = similarity_count(individual.belief, reality_code)
            if individual_similarity > organization_similarity:
            # the definition of superior group
                superior_group.append(individual)
        if len(superior_group) == 0:
            return
        else:
            dominant_belief = get_dominant_belief([individual.belief for individual in superior_group])
        ks = self.calculate_k(superior_group)
        code = list(self.code)
        res = []
        for cur in range(len(code)):
            # According to
            if np.random.uniform(0, 1) > pow((1 - self.adaptation_rate), ks[cur]):
                res.append(dominant_belief[cur])
            else:
                res.append(code[cur])
        self.code = list(res)

    def knowledge_equivalence(self, reality_code):
        res = 0
        for cur in range(len(self.code)):
            if self.code[cur] == reality_code[cur]:
                res += 1
        return res / len(self.code)


def similarity_count(x1, x2):
    """
    Calculate the similarity between two belief
    :param x1:
    :param x2:
    :return: the number of same element in the same position
    """
    res = 0
    for cur in range(len(x1)):
        if x1[cur] == x2[cur]:
            res += 1
    return res


def get_dominant_belief(xs):
    """
    For each domain, get the dominant element (-1, 0, 1)
    :param xs: belief list, to count the dominant element
    :return: the dominant element for each state position
    """
    dic = {cur: [0, 0, 0] for cur in range(len(xs[0]))}
    for x in xs:
        for cur in range(len(x)):
            if x[cur] == -1:
                dic[cur][0] += 1
            elif x[cur] == 0:
                dic[cur][1] += 1
            else:
                dic[cur][2] += 1
    res = []
    for cur in range(len(xs[0])):
        index = dic[cur].index(max(dic[cur]))
        if index == 0:
            res.append(-1)
        elif index == 1:
            res.append(0)
        else:
            res.append(1)
    return res


if __name__ == '__main__':
    ress = []

    for p1 in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        for p2 in [0.1, 0.5, 0.9]:
            print(p1, p2)
            repeat_res = []
            for repeat in range(80):
                reality = Reality(element_num=30)
                individuals = []
                for cur in range(50):
                    individuals.append(Individual(30, p1))
                organization = Organization(30, individuals, p2)
                long_res = []
                for period in range(100):
                    for individual in organization.individuals:
                        individual.socialization(organization.code)
                    organization.adaptation(reality.state)
                    long_res.append(organization.knowledge_equivalence(reality.state))
                repeat_res.append(long_res)
            ress.append(repeat_res)


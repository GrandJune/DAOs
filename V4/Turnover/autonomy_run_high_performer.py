# -*- coding: utf-8 -*-
# @Time     : 10/13/2022 15:20
# @Author   : Junyi
# @FileName: autonomy_run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Autonomy import Autonomy
from Reality import Reality
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle


TURNOVER_MODES = ("random", "low_performer", "high_performer")


def func(m=None, n=None, group_size=None, lr=None, turnover_rate=None, turnover_mode="random",
         search_loop=None, loop=None, return_dict=None, sema=None):
    if turnover_mode not in TURNOVER_MODES:
        raise ValueError("Unsupported turnover_mode: {0}".format(turnover_mode))

    np.random.seed(None)
    reality = Reality(m=m)
    autonomy = Autonomy(m=m, n=n, reality=reality, group_size=group_size, lr=lr)
    for period in range(search_loop):
        # Turbulence
        # if (period + 1) % 100 == 0:
        #     reality.change(reality_change_rate=0.1)
        #     for team in autonomy.teams:
        #         for individual in team.individuals:
        #             individual.payoff = reality.get_payoff(belief=individual.belief)
        # Turnover
        if turnover_rate != 0:
            if (period + 1) % 100 == 0:
                if turnover_mode == "random":
                    autonomy.turnover(turnover_rate=turnover_rate)
                elif turnover_mode in ["low_performer", "high_performer"]:
                    individuals = []
                    for team in autonomy.teams:
                        individuals += team.individuals
                    turnover_num = int(round(turnover_rate * len(individuals)))
                    if turnover_num > 0:
                        reverse = turnover_mode == "high_performer"
                        selected_individuals = sorted(individuals, key=lambda x: x.payoff, reverse=reverse)[:turnover_num]
                        for individual in selected_individuals:
                            individual.turnover(turnover_rate=1)
        autonomy.search()
    return_dict[loop] = [autonomy.performance_across_time, autonomy.diversity_across_time,
                         autonomy.variance_across_time]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    m = 90
    turnover_rate_list = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
    turnover_mode = "high_performer"  # Select from TURNOVER_MODES.
    # TURNOVER_MODES = ("random", "low_performer", "high_performer")
    group_size = 7
    n = 350
    lr = 0.3
    repetition = 500
    concurrency = 100
    search_loop = 500
    # DVs
    # after taking an average across repetitions
    performance_across_para = []
    diversity_across_para = []
    variance_across_para = []

    # retain the time dimension
    # performance_across_para_time = []
    # diversity_across_para_time = []
    # variance_across_para_time = []
    for turnover_rate in turnover_rate_list:
        print("Turnover Rate", turnover_rate,
              time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        return_dict = manager.dict()
        jobs = []
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func,
                           args=(m, n, group_size, lr, turnover_rate, turnover_mode, search_loop, loop,
                                 return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.

        # remove the time dimension, only keep the last value
        performance_across_repeat = [result[0][-1] for result in results]
        diversity_across_repeat = [result[1][-1] for result in results]
        variance_across_repeat = [result[2][-1] for result in results]

        # take an average across repetition, only one value for one parameter
        performance_across_para.append(sum(performance_across_repeat) / len(performance_across_repeat))
        diversity_across_para.append(sum(diversity_across_repeat) / len(diversity_across_repeat))
        variance_across_para.append(sum(variance_across_repeat) / len(variance_across_repeat))

        # keep the time dimension
        # performance_across_repeat_time = [result[0] for result in results]
        # diversity_across_repeat_time = [result[1] for result in results]
        # variance_across_repeat_time = [result[2] for result in results]

        # take an average across repetition, for each time iteration, integrate into [loop] values for one parameter
        # performance_across_time = []  # under the same parameter
        # diversity_across_time = []
        # variance_across_time = []
        # for period in range(search_loop):
        #     temp_performance = [performance_list[period] for performance_list in performance_across_repeat_time]
        #     performance_across_time.append(sum(temp_performance) / len(temp_performance))
        #
        #     temp_diversity = [diversity_list[period] for diversity_list in diversity_across_repeat_time]
        #     diversity_across_time.append(sum(temp_diversity) / len(temp_diversity))
        #
        #     temp_variance = [variance_list[period] for variance_list in variance_across_repeat_time]
        #     variance_across_time.append(sum(temp_variance) / len(temp_variance))

        # retain the time dimension
        # performance_across_para_time.append(performance_across_time)
        # diversity_across_para_time.append(diversity_across_time)
        # variance_across_para_time.append(variance_across_time)

    results_to_save = {
        "performance": performance_across_para,
        "diversity": diversity_across_para,
        "variance": variance_across_para,
    }
    for metric, values in results_to_save.items():
        file_name = "autonomy_{0}_{1}_across_turnover".format(turnover_mode, metric)
        with open(file_name, "wb") as out_file:
            pickle.dump(values, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))  # Duration
    print("Autonomy {0}".format(turnover_mode.replace("_", " ").title()),
          time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))
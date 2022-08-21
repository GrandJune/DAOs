from multiprocessing import Pool
import time
import multiprocessing as mp


def worker(s, return_dict_1):
    print(str(s) + "s represent!")
    return_dict_1[s] = range(s)

def superior(t, return_dict_2):
    manager = mp.Manager()
    return_dict_1 = manager.dict()
    jobs = []
    for i in range(5):
        p = mp.Process(target=worker, args=(i, return_dict_1))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    return_dict_2[t] = return_dict_1.values()


if __name__ == "__main__":
    manager = mp.Manager()
    return_dict_2 = manager.dict()
    jobs = []
    for i in range(5):
        p = mp.Process(target=superior, args=(i, return_dict_2))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    print(return_dict_2.values())

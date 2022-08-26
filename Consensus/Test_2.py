from multiprocessing import Pool
import time
import multiprocessing as mp
from multiprocessing import pool


def worker(s, ):
    print(str(s) + "s represent!")
    return range(s)



if __name__ == "__main__":
    manager = mp.Manager()

    return_dict_2 = manager.dict()
    cpu_num = mp.cpu_count()
    print("cpu_num: ", cpu_num)
    pool = Pool(cpu_num)
    result_list = []
    for i in range(20):
        result_list.append(pool.apply_async(func=worker, args=(i, )).get())
        print("********")
    print(result_list)

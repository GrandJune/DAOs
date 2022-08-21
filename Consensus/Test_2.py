from multiprocessing import Pool
import time
import multiprocessing as mp


# def worker(s, return_dict):
#     print(str(s) + " represent!")
#     return_dict[s] = range(s)
#
#
# if __name__ == "__main__":
#     manager = mp.Manager()
#     return_dict = manager.dict()
#     jobs = []
#     for i in range(5):
#         p = mp.Process(target=worker, args=(i, return_dict))
#         jobs.append(p)
#         p.start()
#
#     for proc in jobs:
#         proc.join()
#     print(return_dict.values())

# confirm = 1.0
confirm = False
if confirm:
    print(confirm)
else:
    print("No")
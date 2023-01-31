# -*- coding: utf-8 -*-
# @Time     : 1/31/2023 14:03
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style

def func(in_list=None):
    in_list_sorted = in_list.copy()
    in_list_sorted.sort( reverse=True)
    # print(in_list_sorted)
    out_list = [in_list_sorted.index(each) + 1 for each in in_list]
    # print(out_list)
    return out_list

if __name__ == '__main__':
    test = [1, 2, 100, -5]
    output = func(in_list=test)
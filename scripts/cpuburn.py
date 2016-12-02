#!/usr/bin/env python

import multiprocessing

def f(x):
    while True:
        x * x

n = multiprocessing.cpu_count()

p = multiprocessing.Pool(processes=n)
p.map(f, range(n))

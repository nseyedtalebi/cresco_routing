# coding: utf-8
T_s = (set(t) for t in powerset(T) if set(t) != set(T) and set(t) != set())

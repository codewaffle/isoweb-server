from time import perf_counter

start = perf_counter()

def clock():
    return perf_counter() - start

print('clockin it')
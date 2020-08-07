from matplotlib import pyplot as plt
from util.what2 import ScheduledTask
import time


lst = []
t0 = time.time()


def func():
    global lst, t0
    t = time.time()
    dt = t - t0
    t0 = t
    lst.append(dt)
    time.sleep(0.25)


def main():
    task = ScheduledTask(0.003, func)
    task.start(delay=1)
    time.sleep(5)
    task.stop()
    time.sleep(1)
    plt.figure()
    plt.plot(lst[1:])
    plt.show()
    for i in lst[1:]:
        print(i)
    print(task.interval)


if __name__ == '__main__':
    main()

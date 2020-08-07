import threading
import time


class ScheduledTask:

    def __init__(self, interval, task, *args, adaptive_interval=False, **kwargs):
        self.interval = interval
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.adaptive_interval = adaptive_interval
        self.shutdown = False
        self.thread = threading.Thread(target=self._run)
        self.t = 0

    def _run(self):
        while not self.shutdown:
            try:
                time.sleep((self.t - time.time()) * 0.8)
                while self.t >= time.time():
                    pass
            except ValueError as e:
                print('value_error')
                if self.adaptive_interval:
                    self.interval *= 1.01
            finally:
                self.t += self.interval
                self.task(*self.args, **self.kwargs)

    def start(self, delay=0.0):
        self.shutdown = False
        self.t = time.time() + delay
        self.thread.start()

    def stop(self):
        self.shutdown = True


ival = 0.001
n = 1
t0 = {key: time.time() for key in range(n)}
lst = []


def main():
    global n, t0, lst, ival

    def func(id):
        t = time.time()
        dt = t - t0[id]
        t0[id] = t
        lst.append((id, dt, dt-ival))

    tasks = []
    for i in range(n):
        task = ScheduledTask(ival, func, i)
        task.start(delay=1)
        tasks.append(task)
    time.sleep(10)
    for t in tasks:
        t.stop()
    for i in lst:
        print(i)
    mean = sum([y for x, y, z in lst[1:]]) / len(lst)
    minn = min([y for x, y, z in lst[1:]])
    maxx = max([y for x, y, z in lst[1:]])

    print(mean, minn, maxx)


if __name__ == '__main__':
    main()
    # TODO workout precision of time.time() how many decimal places, what resolution. Micros better?

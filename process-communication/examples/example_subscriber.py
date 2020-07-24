import proccom
from threading import Thread
import time


def break_cmd():
    stop = False
    while not stop:
        a = input()
        if a == 'q':
            stop = True


def handler(msg):
    print(msg, time.time())


def main():
    break_thread = Thread(target=break_cmd, daemon=False)
    break_thread.start()
    subscriber = proccom.Subscriber({'test_topic': handler}, 'test_subscriber')
    subscriber.connect()
    stop = False
    while not stop:
        time.sleep(1)
        if not break_thread.is_alive():
            stop = True
    subscriber.stop()


if __name__ == '__main__':
    main()

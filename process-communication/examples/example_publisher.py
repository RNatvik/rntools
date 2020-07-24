import proccom
from threading import Thread
import time


def break_cmd():
    stop = False
    while not stop:
        a = input()
        if a == 'q':
            stop = True


def main():
    break_thread = Thread(target=break_cmd, daemon=False)
    break_thread.start()
    publisher = proccom.Publisher('test_topic', 'test_publisher', proccom.msgs.format_test)
    publisher.connect()
    stop = False
    while not stop:
        time.sleep(1)
        publisher.publish(1, 2, 3)
        if not break_thread.is_alive():
            stop = True
    publisher.stop()


if __name__ == '__main__':
    main()

import time
import os


def timed(func):
    """
    This decorator adds a timer to the decorated function. The original function results and the timer results
    are returned as a tuple of size 2
    :param func: the function to decorate
    :return: decorated function
    """
    def timed_method(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        return result, total_time
    return timed_method


def dir_active(directory):
    """
    This decorator changes the current working directory to the provided directory parameter
    :param directory: the target working directory (i.e __file__)
    :return: decorated function
    """
    if callable(directory):
        raise TypeError(f'dir_active decorator parameter is not set. Parameter directory = {directory}')

    def decorator(func):
        def wrapper(*args, **kwargs):
            path = os.path.dirname(os.path.abspath(directory))
            os.chdir(path)
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


def clean_exit(exit_func):
    """
    This decorator takes a function as a parameter which will be called if a keyboarad interrupt exception is caugth
    :param exit_func: the function to call if keyboard interrupt
    :return: result of decorated function OR None if exception is caught
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = None
            try:
                result = func(*args, **kwargs)
            except KeyboardInterrupt:
                exit_func()
            return result
        return wrapper
    return decorator
